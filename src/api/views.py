import uuid
import json
import logging
import asyncio
from json import JSONDecodeError

import aioredis
from aiohttp import web
from aiopg.pool import create_pool

from common import JobStatus, QUEUE_HIGH, DB_DSN, REDIS_HOST

logger = logging.getLogger('http')
logger.setLevel(logging.INFO)


def bad_request_response(msg=''):
    msg += '\n'
    return web.HTTPBadRequest(body=msg.encode())


def json_bytes(data, pretty=False):
    if pretty:
        s = json.dumps(data, indent=2) + '\n'
    else:
        s = json.dumps(data)
    return s.encode()


def get_ip(request):
    peername = request.transport.get_extra_info('peername')
    ip = '-'
    if peername is not None:
        ip, _ = peername
    return ip


class APIController:
    pg_pool = None
    redis = None

    def __init__(self, app):
        self.app = app
        self.loop = app._loop
        self.add_routes()
        self.add_middleware()

    def _til_complete(self, future):
        return self.loop.run_until_complete(future)

    def add_routes(self):
        self.app.router.add_route('POST', '/generate', self.generate_pdf)

    def add_middleware(self):
        async def auth_middleware_factory(app, handler):
            async def auth_middleware(request):
                log_extra = {'ip': get_ip(request)}
                if 'Authorization' not in request.headers:
                    logger.info('bad request: %s', 'no auth header', extra=log_extra)
                    return bad_request_response('No "Authorization" header found')

                token = request.headers['Authorization'].replace('Token ', '')
                organisation = await self.check_token(token)
                if organisation is None:
                    logger.info('forbidden request: invalid token "%s"', token, extra=log_extra)
                    return web.HTTPForbidden(body='Invalid Authorization token\n'.encode())
                request.organisation = organisation
                request.log_extra = log_extra
                return await handler(request)
            return auth_middleware

        self.app._middlewares = [auth_middleware_factory]

    async def generate_pdf(self, request):
        data = await request.content.read()
        data = data.decode()
        try:
            obj = json.loads(data)
        except JSONDecodeError as e:
            logger.info('bad request: %s', 'invalid json', extra=request.log_extra)
            return bad_request_response('Error Decoding JSON: {}'.format(e))

        if 'template' not in obj:
            logger.info('bad request: %s', 'no template', extra=request.log_extra)
            return bad_request_response('"template" not found in request JSON: "{}"'.format(data))
        # TODO: check template belongs to correct org, get template from name
        template = obj['template']

        if 'html' not in obj:
            logger.info('bad request: %s', 'no html', extra=request.log_extra)
            return bad_request_response('"html" not found in request JSON: "{}"'.format(data))

        job_id = await self.create_job(template)
        await self.add_to_queue(job_id, obj['html'])

        logger.info('good request: job created, %s', job_id, extra=request.log_extra)
        response = {'job_id': job_id, 'status': JobStatus.STATUS_PENDING}
        return web.Response(body=json_bytes(response, True), status=201, content_type='application/json')

    async def check_token(self, token):
        cur = await self.execute('SELECT id FROM orgs_organisation '
                                 'INNER JOIN orgs_apikey ON orgs_organisation.id = orgs_apikey.org_id WHERE '
                                 'orgs_apikey.key = %s', [token])
        org = await cur.fetchone()
        return org

    async def create_job(self, template_id):
        id = str(uuid.uuid4())
        await self.execute('INSERT INTO jobs_job (id, template_id) VALUES (%s, %s);', [id, template_id])
        return id

    @asyncio.coroutine
    def execute(self, *args, **kwargs):
        if self.pg_pool is None:
            self.pg_pool = yield from create_pool(DB_DSN, loop=self.loop, minsize=2, maxsize=10)

        with (yield from self.pg_pool) as conn:
            cur = yield from conn.cursor()
            yield from cur.execute(*args, **kwargs)
            return cur

    async def add_to_queue(self, job_id, html):
        self.redis = self.redis or await aioredis.create_redis((REDIS_HOST, 6379), loop=self.loop)
        data = {
            'job_id': job_id,
            'html': html
        }
        await self.redis.rpush(QUEUE_HIGH, json_bytes(data))

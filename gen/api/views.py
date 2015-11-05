import uuid
import json
import logging
import asyncio
from json import JSONDecodeError

import aioredis
from aiohttp import web
from aiopg.pool import create_pool

from common import JobStatus, QUEUE_HIGH, DB_DSN

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

    def _til_complete(self, future):
        return self.loop.run_until_complete(future)

    def add_routes(self):
        self.app.router.add_route('POST', '/generate', self.generate_pdf)

    async def generate_pdf(self, request):
        log_extra = {'ip': get_ip(request)}
        if 'Authorization' not in request.headers:
            logger.info('bad request: %s', 'no auth header', extra=log_extra)
            return bad_request_response('No "Authorization" header found')

        token = request.headers['Authorization'].replace('Token ', '')
        organisation = await self.check_token(token)
        if organisation is None:
            logger.info('forbidden request: invalid token "%s"', token, extra=log_extra)
            return web.HTTPForbidden(body='Invalid Authorization token\n'.encode())

        try:
            obj = await request.json()
        except JSONDecodeError as e:
            logger.info('bad request: %s', 'invalid json', extra=log_extra)
            return bad_request_response('Error Decoding JSON: {}'.format(e))

        if 'html' not in obj:
            logger.info('bad request: %s', 'no html', extra=log_extra)
            return bad_request_response('"html" not found in request JSON: {}'.format(obj))

        job_id = await self.create_job(org_id=organisation)
        await self.add_to_queue(job_id, obj['html'])

        logger.info('good request: job created, %s', job_id, extra=log_extra)
        response = {'job_id': job_id, 'status': JobStatus.STATUS_PENDING}
        return web.Response(body=json_bytes(response, True), status=201, content_type='application/json')

    async def check_token(self, token):
        cur = await self.execute('SELECT id FROM jobs_organisation INNER JOIN jobs_apikey ON '
                                 '(jobs_organisation.id = jobs_apikey.org_id) WHERE '
                                 'jobs_apikey.key = %s', [token])
        org = await cur.fetchone()
        return org

    async def create_job(self, org_id):
        id = str(uuid.uuid4())
        await self.execute('INSERT INTO jobs_job (id, org_id) VALUES (%s, %s);', [id, org_id])
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
        self.redis = self.redis or await aioredis.create_redis(('localhost', 6379), loop=self.loop)
        data = {
            'job_id': job_id,
            'html': html
        }
        self.redis.rpush(QUEUE_HIGH, json_bytes(data))

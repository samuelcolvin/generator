import os
import uuid
import json
import logging
from json import JSONDecodeError

import aioredis
from aiohttp import web

from common import JobStatus, QUEUE_HIGH, PGCon, BASE_DIR, DEBUG, loop

logger = logging.getLogger('http')
logger.setLevel(logging.INFO)

pg_con = PGCon()


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


async def check_token(token):
    cur = await pg_con.execute("SELECT id FROM jobs_organisation INNER JOIN jobs_apikey ON "
                               "(jobs_organisation.id = jobs_apikey.org_id) WHERE "
                               "jobs_apikey.key = %s", [token])
    org = await cur.fetchone()
    return org


async def create_job(org_id):
    id = str(uuid.uuid4())
    await pg_con.execute('INSERT INTO jobs_job (id, org_id) VALUES (%s, %s);', [id, org_id])
    return id


async def add_to_queue(job_id, html):
    redis = await aioredis.create_redis(('localhost', 6379), loop=loop)
    data = {
        'job_id': job_id,
        'html': html
    }
    redis.rpush(QUEUE_HIGH, json_bytes(data))
    redis.close()


async def generate_pdf(request):
    log_extra = {'ip': get_ip(request)}
    if 'Authorization' not in request.headers:
        logger.info('bad request: %s', 'no auth header', extra=log_extra)
        return bad_request_response('No "Authorization" header found')

    token = request.headers['Authorization'].replace('Token ', '')
    organisation = await check_token(token)
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

    job_id = await create_job(org_id=organisation)
    await add_to_queue(job_id, obj['html'])

    logger.info('good request: job created, %s', job_id, extra=log_extra)
    response = {'job_id': job_id, 'status': JobStatus.STATUS_PENDING}
    return web.Response(body=json_bytes(response, True), status=201, content_type='application/json')


if DEBUG:
    FILE_STORE_PATH = os.path.join(BASE_DIR, '../fake_file_store')
    if not os.path.exists(FILE_STORE_PATH):
        os.mkdir(FILE_STORE_PATH)

    async def fake_file_storage(request):
        """
        Worker "uploads" files here when being tested, to avoid files having to go to s3
        """
        data = await request.post()
        file_data = data['pdf_file']

        filename = file_data.filename
        file_path = os.path.join(FILE_STORE_PATH, filename)
        with open(file_path, 'wb') as f:
            f.write(file_data.file.read())

        log_extra = {'ip': get_ip(request)}
        url = 'http://path2.com/{}'.format(filename)
        logger.info('fake file stored, url: %s', url, extra=log_extra)
        response = {
            'url': url
        }
        return web.Response(body=json_bytes(response, True), status=201, content_type='application/json')

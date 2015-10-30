import asyncio
import uuid
import json
from json import JSONDecodeError

import aioredis
from aiohttp import web

from common import JobStatus, QUEUE_HIGH, PGCon

loop = asyncio.get_event_loop()

pg_con = PGCon()


def bad_request_response(msg=''):
    msg += '\n'
    return web.HTTPBadRequest(body=msg.encode())


def json_bytes(data):
    return json.dumps(data).encode()


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
    if 'Authorization' not in request.headers:
        return bad_request_response('No "Authorization" header found')

    token = request.headers['Authorization'].replace('Token ', '')
    organisation = await check_token(token)
    if organisation is None:
        return web.HTTPForbidden(body='Invalid Authorization token\n'.encode())

    try:
        obj = await request.json()
    except JSONDecodeError as e:
        return bad_request_response('Error Decoding JSON: {}'.format(e))

    if 'html' not in obj:
        return bad_request_response('"html" not found in request JSON: {}'.format(obj))

    job_id = await create_job(org_id=organisation)
    await add_to_queue(job_id, obj['html'])

    response = {'job_id': job_id, 'status': JobStatus.STATUS_PENDING}
    return web.Response(body=json_bytes(response))

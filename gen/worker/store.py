import os
import asyncio

import aiohttp
import boto
from boto.s3.key import Key

from common import DEBUG, S3_KEY, S3_SECRET

loop = asyncio.get_event_loop()  # FIXME

async def fake_store(job_id, org_code, file_name):
    files = {'pdf_file': open(file_name, 'rb')}
    async with aiohttp.post('http://localhost:8000/fakestorage', data=files) as r:
        data = await r.json()
        return data['url']


def s3_conn():
    return boto.connect_s3(S3_KEY, S3_SECRET)


async def s3_store(job_id, org_code, file_name):
    return await loop.run_in_executor(None, _s3_store_blocking, job_id, org_code, file_name)


def _s3_store_blocking(job_id, org_code, file_name):
    # TODO this method needs altering to be properly asynchronous once a good boto asynchronous library is available
    bucket = 'pdf-gen-test'
    key = os.path.join(org_code, job_id +'.pdf')
    k = Key(s3_conn().get_bucket(bucket))
    k.key = key
    k.set_contents_from_filename(file_name)


def get_temporary_url(job_id, org_code):
    key = os.path.join(org_code, job_id +'.pdf')
    url = s3_conn().generate_url(600, 'GET', bucket_name, key)
    return


async def store_file(job_id, org_code, file_name):
    if DEBUG:
        return await fake_store(job_id, org_code, file_name)
    else:
        return await s3_store(job_id, org_code, file_name)

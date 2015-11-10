import asyncio
import traceback
import json.decoder

from django.utils import timezone

from common import QUEUE_HIGH
from dj.jobs.models import Organisation, Job


async def test_run_worker(worker):
    await asyncio.sleep(0.1, loop=worker.loop)


async def test_simple_job(redis, db, worker, mocker):
    job_id = org_code = file_content = None
    async def fake_s3_store(*args):
        nonlocal job_id, org_code, file_content
        job_id, org_code, file_name = args
        with open(file_name, 'rb') as f:
            file_content = f.read()
    mocker.patch('worker.store.s3_store', side_effect=fake_s3_store)
    org = Organisation.objects.create(name='test organisation')
    job = Job.objects.create(org=org, timestamp_created=timezone.now())
    data = '{"job_id": "%s", "html": "<h1>hello</h1>"}' % job.id
    redis.rpush(QUEUE_HIGH, data.encode())
    for i in range(10):
        if job_id is not None:
            break
        await asyncio.sleep(0.1, loop=worker.loop)

    assert job_id == str(job.id)
    assert org_code == org.code
    assert file_content.startswith(b'%PDF-')
    assert worker.exc_info is None, traceback.print_exception(*worker.exc_info)


async def test_bad_job(redis, worker):
    redis.rpush(QUEUE_HIGH, b'foo bar')
    for i in range(10):
        if worker.exc_info is not None:
            break
        await asyncio.sleep(0.1, loop=worker.loop)

    assert worker.exc_info is not None
    assert worker.exc_info[0] == json.decoder.JSONDecodeError
    assert str(worker.exc_info[1]) == 'Expecting value: line 1 column 1 (char 0)'

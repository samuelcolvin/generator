import os
import json
import asyncio
from asyncio import Semaphore

import aioredis
from common import JobStatus, QUEUES, PGCon, MAX_WORKER_THREADS, MAX_WORKER_JOBS, loop
from .pdf import generate_pdf
from .store import store_file

pg_con = PGCon()
wkh2p_sema = Semaphore(value=MAX_WORKER_THREADS, loop=loop)
worker_sema = Semaphore(value=MAX_WORKER_JOBS, loop=loop)


async def job_in_progress(job_id):
    ctx = [JobStatus.STATUS_IN_PROGRESS, job_id]
    await pg_con.execute('UPDATE jobs_job SET status=%s, timestamp_started=current_timestamp WHERE id=%s;', ctx)


async def job_finished(job_id, html, file_size):
    ctx = [JobStatus.STATUS_COMPLETE, html, file_size, job_id]
    await pg_con.execute('UPDATE jobs_job SET status=%s, timestamp_complete=current_timestamp, '
                         'html=%s, file_size=%s WHERE id=%s;', ctx)


async def get_organisation_code(job_id):
     cur = await pg_con.execute("SELECT jobs_organisation.code FROM jobs_organisation INNER JOIN jobs_job ON "
                                "(jobs_organisation.id = jobs_job.org_id) WHERE "
                                "jobs_job.id = %s", [job_id])
     org = await cur.fetchone()
     return org


async def work(raw_data):
    """
    Do job, data shape:
    {
        'job_id': UUID of job,
        'content': JSON object to use in template
        OR
        'html': HTML to generate pdf for
    }
    :param raw_data: json bytes
    :return:
    """
    text = raw_data.decode('utf8')
    data = json.loads(text)
    job_id = data['job_id']
    print('doing {}'.format(job_id))
    await job_in_progress(job_id)
    content = data.get('content')
    if content:
        raise NotImplementedError()
        # TODO generate html
    else:
        html = data['html']
    await wkh2p_sema.acquire()
    pdf_file = await loop.run_in_executor(None, generate_pdf, html)
    wkh2p_sema.release()

    # the temporary file is not automatically deleted, so we need to make sure we do it here
    try:
        file_size = os.path.getsize(pdf_file)
        await store_file(pdf_file, organisation_code)
    finally:
        os.remove(pdf_file)
    await job_finished(job_id, html, file_size)
    worker_sema.release()


async def work_loop():
    # TODO deal with SIGTERM gracefully
    redis = await aioredis.create_redis(('localhost', 6379), loop=loop)
    try:
        while True:
            await worker_sema.acquire()
            queue, data = await redis.blpop(*QUEUES)
            asyncio.ensure_future(work(data))
    finally:
        redis.close()


def run_worker():
    loop.run_until_complete(work_loop())

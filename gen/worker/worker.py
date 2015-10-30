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


async def update_job_status(job_id, status):
    ctx = [status, job_id]
    await pg_con.execute('UPDATE jobs_job SET status=%s, timestamp_started=current_timestamp WHERE id=%s;', ctx)


async def update_job_finished(job_id, pdf_url, html, file_size):
    ctx = [JobStatus.STATUS_COMPLETE, pdf_url, html, file_size, job_id]
    await pg_con.execute('UPDATE jobs_job SET status=%s, timestamp_complete=current_timestamp, file_link=%s, '
                         'html=%s, file_size=%s WHERE id=%s;', ctx)


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
    await update_job_status(job_id, JobStatus.STATUS_IN_PROGRESS)
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
        pdf_url = await store_file(pdf_file)
    finally:
        os.remove(pdf_file)
    await update_job_finished(job_id, pdf_url, html, file_size)
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

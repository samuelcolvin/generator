import json
import asyncio
from threading import BoundedSemaphore

import aioredis
from common import JobStatus, QUEUES, PGCon, MAX_WORKER_THREADS, loop
from .pdf import generate_pdf

pg_con = PGCon()
thread_sema = BoundedSemaphore(value=MAX_WORKER_THREADS)

async def update_status(job_id, status):
    await pg_con.execute('UPDATE jobs_job SET status=%s WHERE id=%s;', [status, job_id])


async def update_html(job_id, new_html):
    ctx = [JobStatus.STATUS_HTML_GENERATED, new_html, job_id]
    await pg_con.execute('UPDATE jobs_job SET status=%s, html=%s WHERE id=%s;', ctx)


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
    await update_status(job_id, JobStatus.STATUS_IN_PROGRESS)
    print('html {}'.format(data['html']))
    content = data.get('content')
    if content:
        raise NotImplementedError()
        # TODO generate html
    else:
        html = data['html']
    await update_html(job_id, html)
    thread_sema.acquire()
    pdf_data = await loop.run_in_executor(None, generate_pdf, html)
    thread_sema.release()
    # TODO send pdf to storage eg. S3
    # TODO update job status in pg, inc. storage url and date
    await asyncio.sleep(5)
    print(type(pdf_data))
    print('finished, pdf len:', len(pdf_data))


def run_worker():
    # TODO deal with SIGTERM gracefully
    async def go():
        redis = await aioredis.create_redis(('localhost', 6379), loop=loop)
        while True:
            queue, data = await redis.blpop(*QUEUES)
            asyncio.ensure_future(work(data))
            # await task
        redis.close()

    loop.run_until_complete(go())

import os
import sys
import json
import logging
import asyncio
from asyncio import Semaphore

from aiopg.pool import create_pool
import aioredis

from common import JobStatus, QUEUES, MAX_WORKER_THREADS, MAX_WORKER_JOBS, DB_DSN, REDIS_HOST
from .pdf import generate_pdf
from .store import store_file

logger = logging.getLogger('worker')
logger.setLevel(logging.DEBUG)


class Worker:
    def __init__(self, loop=None):
        logger.info('Worker initialising...')
        loop = loop or asyncio.get_event_loop()
        self.loop = loop
        logger.debug('Connecting to db: "%s"', DB_DSN)
        self._pool = loop.run_until_complete(create_pool(dsn=DB_DSN, loop=loop, minsize=2, maxsize=10))
        self.wkh2p_sema = Semaphore(value=MAX_WORKER_THREADS, loop=loop)
        self.worker_sema = Semaphore(value=MAX_WORKER_JOBS, loop=loop)
        self.redis = None
        self.exc_info = None

    def run_forever(self):
        self.loop.run_until_complete(self.work_loop())

    async def work_loop(self):
        # TODO deal with SIGTERM gracefully
        logger.debug('Connecting to redis on: "%s"', REDIS_HOST)
        self.redis = await aioredis.create_redis((REDIS_HOST, 6379), loop=self.loop)
        logger.info('Worker started...')
        try:
            while True:
                await self.worker_sema.acquire()
                queue, data = await self.redis.blpop(*QUEUES)
                asyncio.ensure_future(self.work_handler(queue, data), loop=self.loop)
        finally:
            self.redis.close()

    async def work_handler(self, queue, raw_data):
        try:
            await self.work(queue, raw_data)
        except:
            logger.error('error processing job: %s', sys.exc_info()[1])
            self.exc_info = sys.exc_info()

    async def work(self, queue_raw, raw_data):
        """
        Do job, data shape:
        {
            'job_id': UUID of job,
            THEN
            'content': JSON object to use in template
            OR
            'html': HTML to generate pdf for
        }
        :param queue_raw: queue name bytes
        :param raw_data: json bytes
        :return:
        """
        queue = queue_raw.decode()
        data = raw_data.decode()
        logger.debug('starting job from queue "%s" with data "%s"', queue, data)
        data = json.loads(data)
        job_id = data['job_id']
        org_code = await self.get_organisation_code(job_id)
        logger.info('starting job - %s for %s', job_id, org_code)
        await self.job_in_progress(job_id)
        content = data.get('content')
        if content:
            raise NotImplementedError()
            # TODO generate html
        else:
            html = data['html']
        await self.wkh2p_sema.acquire()
        pdf_file = await self.loop.run_in_executor(None, generate_pdf, html)
        self.wkh2p_sema.release()
        logger.info('pdf generated - %s for %s', job_id, org_code)

        # the temporary file is not automatically deleted, so we need to make sure we do it here
        try:
            file_size = os.path.getsize(pdf_file)
            await store_file(job_id, org_code, pdf_file)
        finally:
            os.remove(pdf_file)
        await self.job_finished(job_id, html, file_size)
        logger.info('finishing job - %s for %s', job_id, org_code)
        self.worker_sema.release()

    async def job_in_progress(self, job_id):
        ctx = [JobStatus.STATUS_IN_PROGRESS, job_id]
        await self.execute('UPDATE jobs_job SET status=%s, timestamp_started=current_timestamp WHERE id=%s;', ctx)

    async def job_finished(self, job_id, html, file_size):
        ctx = [JobStatus.STATUS_COMPLETE, html, file_size, job_id]
        await self.execute('UPDATE jobs_job SET status=%s, timestamp_complete=current_timestamp, '
                           'html=%s, file_size=%s WHERE id=%s;', ctx)

    async def get_organisation_code(self, job_id):
        cur = await self.execute('SELECT jobs_organisation.code FROM jobs_organisation INNER JOIN jobs_job ON '
                                 '(jobs_organisation.id = jobs_job.org_id) WHERE '
                                 'jobs_job.id = %s', [job_id])
        org = await cur.fetchone()
        return org[0]

    @asyncio.coroutine
    def execute(self, *args, **kwargs):
        with (yield from self._pool) as conn:
            cur = yield from conn.cursor()
            yield from cur.execute(*args, **kwargs)
            return cur

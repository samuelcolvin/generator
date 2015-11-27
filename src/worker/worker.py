import os
import sys
import json
import logging
import asyncio
from asyncio import Semaphore

from aiopg.pool import create_pool
from psycopg2.extras import DictCursor
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
                self.loop.create_task(self.work_handler(queue, data))
        finally:
            self.redis.close()

    async def work_handler(self, queue, raw_data):
        try:
            await self.work(queue, raw_data)
        except:
            logger.error('error processing job: %s', sys.exc_info()[1])
            self.exc_info = sys.exc_info()
            raise

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
        org_code, env_id = await self.get_basic_info(job_id)
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

    async def get_basic_info(self, job_id):
        cur = await self.execute(
            'SELECT orgs_organisation.code, resources_env.id FROM orgs_organisation '
            'INNER JOIN resources_env ON orgs_organisation.id = resources_env.org_id '
            'INNER JOIN jobs_job ON resources_env.id = jobs_job.env_id WHERE '
            'jobs_job.id = %s', [job_id])
        org, env_id = await cur.fetchone()
        return org, env_id

    async def get_env_info(self, job_id, env_id):
        cur = await self.execute(
            'SELECT r_main.ref AS main_ref, r_main.file AS main_file, '
            'r_base.ref as base_ref, r_base.file as base_file, '
            'r_base.ref as header_ref, r_header.file as header_file, '
            'r_base.ref as footer_ref, r_footer.file as footer_file '
            'FROM resources_env '
            'JOIN resources_file AS r_main ON r_main.id = resources_env.main_template_id '
            'JOIN resources_file AS r_base ON r_base.id = resources_env.base_template_id '
            'JOIN resources_file AS r_header ON r_header.id = resources_env.header_template_id '
            'JOIN resources_file AS r_footer ON r_footer.id = resources_env.footer_template_id '
            'WHERE resources_env.id = %s', [env_id], dict_cursor=True)
        data = dict(await cur.fetchone())
        print(data)
        # FIXME, work stopped here

    @asyncio.coroutine
    def execute(self, *args, **kwargs):
        cursor_factory = kwargs.pop('dict_cursor', None) and DictCursor
        with (yield from self._pool) as conn:
            cur = yield from conn.cursor(cursor_factory=cursor_factory)
            yield from cur.execute(*args, **kwargs)
            return cur

import os
import asyncio
import logging
from aiopg.pool import create_pool

DEBUG = True

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DATABASE = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'generator',
    'USER': 'postgres',
    'PASSWORD': 'waffle',
    'HOST': 'localhost',
    'PORT': '',
    'CONN_MAX_AGE': None
}

DB_DSN = 'dbname={NAME} user={USER} password={PASSWORD} host={HOST} port={PORT}'.format(**DATABASE)

QUEUE_HIGH = 'queue:high'
QUEUE_MEDIUM = 'queue:medium'
QUEUE_LOW = 'queue:medium'
QUEUES = [
    QUEUE_HIGH,
    QUEUE_MEDIUM,
    QUEUE_LOW,
]

MAX_WORKER_THREADS = 2
MAX_WORKER_JOBS = 5

S3_KEY = os.getenv('S3_KEY')
S3_SECRET = os.getenv('S3_SECRET')

loop = asyncio.get_event_loop()


class JobStatus:
    STATUS_PENDING = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETE = 'complete'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'pending'),
        (STATUS_IN_PROGRESS, 'in_progress'),
        (STATUS_COMPLETE, 'complete'),
    )


class PGCon:
    def __init__(self):
        self._pool = loop.run_until_complete(create_pool(DB_DSN, minsize=2, maxsize=10))

    @asyncio.coroutine
    def execute(self, *args, **kwargs):
        with (yield from self._pool) as conn:
            cur = yield from conn.cursor()
            yield from cur.execute(*args, **kwargs)
            return cur

stream_handler = logging.StreamHandler()
stream_handler.setLevel(logging.DEBUG)
stream_handler.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(ip)s %(levelname)s - %(message)s'))
http_logger = logging.getLogger('http')
http_logger.addHandler(stream_handler)

try:
    from localsettings import *
except ImportError:
    pass

import asyncio

from aiopg.pool import create_pool

from dj.settings import DATABASES


DB_DSN = 'dbname={NAME} user={USER} password={PASSWORD} host={HOST} port={PORT}'.format(**DATABASES['default'])


class JobStatus:
    STATUS_PENDING = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_HTML_GENERATED = 'html_generated'
    STATUS_COMPLETE = 'complete'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'pending'),
        (STATUS_IN_PROGRESS, 'in_progress'),
        (STATUS_HTML_GENERATED, 'html_generated'),
        (STATUS_COMPLETE, 'complete'),
    )

QUEUE_HIGH = 'queue:high'
QUEUE_MEDIUM = 'queue:medium'
QUEUE_LOW = 'queue:medium'
QUEUES = [
    QUEUE_HIGH,
    QUEUE_MEDIUM,
    QUEUE_LOW,
]

MAX_WORKER_THREADS = 2

loop = asyncio.get_event_loop()


class PGCon:
    def __init__(self):
        self._pool = loop.run_until_complete(create_pool(DB_DSN))

    @asyncio.coroutine
    def execute(self, *args, **kwargs):
        with (yield from self._pool) as conn:
            cur = yield from conn.cursor()
            yield from cur.execute(*args, **kwargs)
            return cur

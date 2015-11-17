import os
import sys

from logs import setup_log_handlers

TESTING = 'py.test' in ' '.join(sys.argv)
DEBUG = not TESTING
DOCKER = 'DOCKER' in os.environ

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

setup_log_handlers()

DATABASE = {
    'ENGINE': 'django.db.backends.postgresql_psycopg2',
    'NAME': 'generator_test' if TESTING else 'generator',
    'USER': 'postgres',
    'PASSWORD': 'waffle',
    'HOST': os.getenv('POSTGRES_PORT_5432_TCP_ADDR', 'localhost'),
    'PORT': os.getenv('POSTGRES_PORT_5432_TCP_PORT', ''),
    'CONN_MAX_AGE': None
}

DB_DSN = 'dbname={NAME} user={USER} password={PASSWORD} host={HOST} port={PORT}'.format(**DATABASE)

REDIS_HOST = os.getenv('REDIS_PORT_6379_TCP_ADDR', 'localhost')

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


class JobStatus:
    STATUS_PENDING = 'pending'
    STATUS_IN_PROGRESS = 'in_progress'
    STATUS_COMPLETE = 'complete'
    STATUS_CHOICES = (
        (STATUS_PENDING, 'pending'),
        (STATUS_IN_PROGRESS, 'in_progress'),
        (STATUS_COMPLETE, 'complete'),
    )

try:
    from localsettings import *  # NOQA
except ImportError:
    pass

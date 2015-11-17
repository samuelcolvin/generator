import os
import sys
import asyncio
import aiohttp
import gc
import pytest
import socket
from unittest import mock

import psycopg2
from aiohttp import web

PROJECT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src'))
sys.path.append(PROJECT_DIR)

from api.views import APIController
from common import DATABASE
from worker import Worker


def pytest_pycollect_makeitem(collector, name, obj):
    if collector.funcnamefilter(name) and callable(obj):
        return list(collector._genfunctions(name, obj))


def pytest_pyfunc_call(pyfuncitem):
    """
    Run asyncio test functions in an event loop instead of a normal
    function call.
    """
    funcargs = pyfuncitem.funcargs
    if 'loop' in funcargs:
        loop = funcargs['loop']
        testargs = {arg: funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames}
        loop.run_until_complete(pyfuncitem.obj(**testargs))
        return True


@pytest.fixture
def port():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('127.0.0.1', 0))
        return s.getsockname()[1]


@pytest.yield_fixture
def loop(request):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)
    loop.set_debug(False)

    yield loop

    loop.stop()
    loop.run_forever()
    loop.close()
    gc.collect()
    asyncio.set_event_loop(None)


@pytest.yield_fixture
def server(loop, port):
    app = handler = srv = None

    async def create(*, debug=False, ssl_ctx=None, proto='http'):
        nonlocal app, handler, srv
        app = web.Application(loop=loop)
        APIController(app)

        handler = app.make_handler(debug=debug, keep_alive_on=False)
        srv = await loop.create_server(handler, '127.0.0.1', port, ssl=ssl_ctx)
        if ssl_ctx:
            proto += 's'
        url = '{}://127.0.0.1:{}'.format(proto, port)
        print('\nServer started at {}'.format(url))
        return app, url

    yield create

    async def finish():
        await handler.finish_connections()
        await app.finish()
        srv.close()
        await srv.wait_closed()

    loop.run_until_complete(finish())


class Client:
    def __init__(self, loop, url):
        self._session = aiohttp.ClientSession(loop=loop)
        if not url.endswith('/'):
            url += '/'
        self.url = url

    def close(self):
        self._session.close()

    def get(self, path, **kwargs):
        while path.startswith('/'):
            path = path[1:]
        url = self.url + path
        return self._session.get(url, **kwargs)

    def post(self, path, **kwargs):
        while path.startswith('/'):
            path = path[1:]
        url = self.url + path
        return self._session.post(url, **kwargs)

    def ws_connect(self, path, **kwargs):
        while path.startswith('/'):
            path = path[1:]
        url = self.url + path
        return self._session.ws_connect(url, **kwargs)


@pytest.yield_fixture
def client(loop, server):
    app, url = loop.run_until_complete(server())
    client = Client(loop, url=url)
    yield client

    client.close()


def pytest_configure():
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'dj.settings')
    import django
    django.setup()

TEMPLATE_DB_NAME = 'generator_test_template'


@pytest.fixture(scope='session')
def db_setup(request):
    conn = psycopg2.connect('user={USER} password={PASSWORD} host={HOST} port={PORT}'.format(**DATABASE))
    conn.autocommit = True
    cur = conn.cursor()
    cur.execute('DROP DATABASE IF EXISTS {}'.format(TEMPLATE_DB_NAME))
    cur.execute('CREATE DATABASE {}'.format(TEMPLATE_DB_NAME))
    cur.close()
    conn.close()

    with mock.patch.dict('common.DATABASE', {'NAME': TEMPLATE_DB_NAME}):
        from django.core.management import call_command
        from django.db import connections
        print('db name:', connections.databases['default']['NAME'])
        call_command('migrate')


@pytest.fixture(scope='function')
def db(request, db_setup):
    from common import DATABASE
    from django.db import connection
    connection.close()
    conn = psycopg2.connect('user={USER} password={PASSWORD} host={HOST} port={PORT}'.format(**DATABASE))
    conn.autocommit = True
    cur = conn.cursor()
    db_name = DATABASE['NAME']
    cur.execute("SELECT pg_terminate_backend(pg_stat_activity.pid) FROM pg_stat_activity\n"
                "WHERE datname='{}' AND pid <> pg_backend_pid();".format(db_name))
    cur.execute('DROP DATABASE IF EXISTS {}'.format(db_name))
    cur.execute('CREATE DATABASE {} WITH TEMPLATE {}'.format(db_name, TEMPLATE_DB_NAME))
    cur.close()
    conn.close()


@pytest.yield_fixture
def redis():
    import redis
    rcon = redis.Redis()
    yield rcon


@pytest.yield_fixture
def worker(loop):
    worker = Worker(loop)
    task = loop.create_task(worker.work_loop())

    yield worker

    worker.redis.close()
    task.cancel()


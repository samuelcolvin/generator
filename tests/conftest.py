import os
import sys
import asyncio
import aiohttp
import gc
import pytest
import socket


from aiohttp import web

PROJECT_DIR = os.path.abspath(os.path.join(os.path.basename(__file__), os.pardir, 'gen'))
sys.path.append(PROJECT_DIR)

from api.views import APIController


@pytest.fixture
def unused_port():
    def f():
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('127.0.0.1', 0))
            return s.getsockname()[1]
    return f


@pytest.yield_fixture
def loop(request):
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(None)

    yield loop

    loop.stop()
    loop.run_forever()
    loop.close()
    gc.collect()
    asyncio.set_event_loop(None)


@pytest.yield_fixture
def server(loop, unused_port):
    app = handler = srv = None

    async def create(*, debug=False, ssl_ctx=None, proto='http'):
        nonlocal app, handler, srv
        app = web.Application(loop=loop)
        APIController(app)
        port = unused_port()

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
    def __init__(self, session, url):
        self._session = session
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
    client = Client(aiohttp.ClientSession(loop=loop), url=url)
    yield client

    client.close()


@pytest.mark.tryfirst
def pytest_pycollect_makeitem(collector, name, obj):
    if collector.funcnamefilter(name) and callable(obj):
        return list(collector._genfunctions(name, obj))


@pytest.mark.tryfirst
def pytest_pyfunc_call(pyfuncitem):
    """
    Run asyncio marked test functions in an event loop instead of a normal
    function call.
    """
    funcargs = pyfuncitem.funcargs
    loop = funcargs['loop']
    testargs = {arg: funcargs[arg] for arg in pyfuncitem._fixtureinfo.argnames}
    loop.run_until_complete(pyfuncitem.obj(**testargs))
    return True

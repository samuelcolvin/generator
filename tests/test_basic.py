import pytest
from aiohttp import web


@pytest.mark.run_loop
async def test_keepalive_two_requests_success(create_app_and_client):
    app, client = await create_app_and_client(server_params={'debug': True})
    resp1 = await client.post('/generate')
    r = await resp1.read()
    print(r)

    # assert 1 == len(client._session.connector._conns)

import pytest


@pytest.mark.run_loop
async def test_no_auth_header(create_app_and_client):
    app, client = await create_app_and_client()
    r = await client.post('/generate')
    assert r.status == 400
    content = await r.read()
    assert content == b'No "Authorization" header found\n'


@pytest.mark.run_loop
async def test_bad_token(create_app_and_client):
    app, client = await create_app_and_client()
    headers = {'Authorization': 'Token 123'}
    r = await client.post('/generate', headers=headers)
    assert r.status == 403
    content = await r.read()
    assert content == b'Invalid Authorization token\n'

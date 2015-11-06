

async def test_no_auth_header(client):
    r = await client.post('/generate')
    assert r.status == 400
    content = await r.read()
    assert content == b'No "Authorization" header found\n'


async def test_bad_token(client):
    headers = {'Authorization': 'Token 123'}
    r = await client.post('/generate', headers=headers)
    assert r.status == 403
    content = await r.read()
    assert content == b'Invalid Authorization token\n'

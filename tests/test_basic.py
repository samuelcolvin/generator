from dj.jobs.models import Organisation, APIKey


async def test_no_auth_header(client):
    r = await client.post('/generate')
    assert r.status == 400
    content = await r.read()
    assert content == b'No "Authorization" header found\n'


async def test_bad_token_no_keys(client, db):
    headers = {'Authorization': 'Token 321'}
    r = await client.post('/generate', headers=headers)
    assert r.status == 403
    content = await r.read()
    assert content == b'Invalid Authorization token\n'


async def test_bad_token_1_org(client, db):
    org = Organisation.objects.create(name='test organisation')
    APIKey.objects.create(org=org, key='123')
    headers = {'Authorization': 'Token 321'}
    r = await client.post('/generate', headers=headers)
    assert r.status == 403
    content = await r.read()
    assert content == b'Invalid Authorization token\n'


async def test_good_token_no_json(client, db):
    org = Organisation.objects.create(name='test organisation')
    APIKey.objects.create(org=org, key='123')
    headers = {'Authorization': 'Token 123'}
    r = await client.post('/generate', headers=headers)
    assert r.status == 400
    content = await r.read()
    assert content == b'Error Decoding JSON: Expecting value: line 1 column 1 (char 0)\n'


async def test_good_token_good_json(client, db):
    org = Organisation.objects.create(name='test organisation')
    APIKey.objects.create(org=org, key='123')
    headers = {'Authorization': 'Token 123'}
    r = await client.post('/generate', data='{"html": "<h1>hello</h1>"}', headers=headers)
    assert r.status == 201
    content = await r.json()
    assert sorted(content.keys()) == ['job_id', 'status']


async def test_good_token_good_json_missing_html(client, db):
    org = Organisation.objects.create(name='test organisation')
    APIKey.objects.create(org=org, key='123')
    headers = {'Authorization': 'Token 123'}
    r = await client.post('/generate', data='{"other": "<h1>hello</h1>"}', headers=headers)
    assert r.status == 400
    content = await r.read()
    assert content == b'"html" not found in request JSON: "{"other": "<h1>hello</h1>"}"\n'

import aiohttp

from common import DEBUG

async def fake_store(file_name):
    files = {'pdf_file': open(file_name, 'rb')}
    async with aiohttp.post('http://localhost:8000/fakestorage', data=files) as r:
        data = await r.json()
        return data['url']


async def store_file(file_name):
    if DEBUG:
        return await fake_store(file_name)
    else:
        raise NotImplementedError()

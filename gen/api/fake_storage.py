import os
import logging

from aiohttp import web

from common import BASE_DIR


logger = logging.getLogger('fake_storage')
logger.setLevel(logging.INFO)


class FakeStorageController:
    def __init__(self, app):
        self.file_storage_path = os.path.join(BASE_DIR, '../fake_file_store')
        if not os.path.exists(self.file_storage_path):
            os.mkdir(self.file_storage_path)
        app.router.add_route('POST', '/fakestorage', self.fake_file_storage)

    async def fake_file_storage(self, request):
        """
        Worker "uploads" files here when being tested, to avoid files having to go to s3
        """
        data = await request.post()
        file_data = data['pdf_file']

        filename = file_data.filename
        file_path = os.path.join(self.file_storage_path, filename)
        with open(file_path, 'wb') as f:
            f.write(file_data.file.read())

        log_extra = {'ip': get_ip(request)}
        url = 'http://path2.com/{}'.format(filename)
        logger.info('fake file stored, url: %s', url, extra=log_extra)
        response = {
            'url': url
        }
        return web.Response(body=json_bytes(response, True), status=201, content_type='application/json')

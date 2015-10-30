from aiohttp import web

from common import DEBUG
from . import views

app = web.Application()
app.router.add_route('POST', '/generate', views.generate_pdf)
if DEBUG:
    app.router.add_route('POST', '/fakestorage', views.fake_file_storage)

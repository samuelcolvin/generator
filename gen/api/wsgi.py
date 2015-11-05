from aiohttp import web

from common import DEBUG
from .views import APIController

app = web.Application()
APIController(app)
if DEBUG:
    from .fake_storage import FakeStorageController
    FakeStorageController(app)

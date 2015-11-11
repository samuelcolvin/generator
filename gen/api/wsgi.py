import os
import sys

from aiohttp import web

BASE_DIR = os.path.abspath(os.path.join(__file__, '..', '..'))
sys.path.append(BASE_DIR)

from .views import APIController

app = web.Application()
APIController(app)

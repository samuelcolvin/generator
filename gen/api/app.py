from aiohttp import web

from . import views

app = web.Application()
app.router.add_route('POST', '/generate', views.generate_pdf)

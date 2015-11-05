#!/usr/bin/env bash
gunicorn -b 0.0.0.0:8000 -k aiohttp.worker.GunicornWebWorker -t 60 --reload gen.api.wsgi:app

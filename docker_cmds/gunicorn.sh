#!/usr/bin/env bash
echo "delaying gunicorn start by 5 seconds..."
sleep 5
gunicorn -b 0.0.0.0:8000 -k aiohttp.worker.GunicornWebWorker -t 60 --reload api.wsgi:app

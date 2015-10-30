#!/usr/bin/env python
import os
import sys
import click

THIS_DIR = os.path.basename(__file__)
sys.path.append(THIS_DIR)

import worker.worker


@click.group()
def cli():
    pass


@cli.command()
def run_worker():
    click.echo('Running worker...')
    worker.worker.run_worker()


@cli.command()
def test_worker():
    import redis
    rcon = redis.Redis()
    rcon.rpush('queue:high', b'{"a": 1}')


if __name__ == '__main__':
    cli()

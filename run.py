#!/usr/bin/env python
import os
import sys
import click

THIS_DIR = os.path.dirname(__file__)
sys.path.append(os.path.join(THIS_DIR, 'gen'))

from worker import Worker


@click.group()
def cli():
    pass


@cli.command()
def run_worker():
    click.echo('Running worker...')
    Worker().run_forever()


@cli.command()
def test_worker():
    import redis
    rcon = redis.Redis()
    rcon.rpush('queue:high', b'{"a": 1}')


if __name__ == '__main__':
    cli()

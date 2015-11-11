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
def worker():
    Worker().run_forever()


if __name__ == '__main__':
    cli()

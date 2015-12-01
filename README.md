# generator

[![Circle CI](https://circleci.com/gh/samuelcolvin/generator/tree/master.svg?circle-token=b924665daf07d607e259a94d0d3cbe3cd4671c5f)](https://circleci.com/gh/samuelcolvin/generator/tree/master)

https://github.com/sameersbn/docker-squid

* environments, eg. collection of files used to gen:
* django interface for users
* remote ftp/webhook/S3 support to return PDF docs.
* notification about complete documents:
  * webhook response to complete documents
  * websockets? Might be harder to know how much time a company is using up.
* pricing structure, probably based on server time spent and storage amount
* extra PDF features (particularly things that are normally hard to achieve):
  * page size
  * signing documents
  * page ordering eg. booklet
  * PDF forms. Maybe no one sane would use these?

wkhtmltopdf `--disable-local-file-access`

## Setup

To install the virtualenv:

    virtualenv -p /usr/bin/python3.5 env

To build the docker image:

    docker build -t gen:v1 .

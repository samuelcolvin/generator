# generator


https://github.com/jettify/aiobotocore
https://pypi.python.org/pypi/aio-s3/0.1

https://github.com/sameersbn/docker-squid

* working with docker.
* environments, eg. collection of files used to gen:
  * static files
  * mustache templating
  * jinja2 templating inc. imported files
  * footer/header integration. How do we do this most clearly?
* S3 support
* django interface for users
* best way to deal with dynamic images in documents? other upload, url encoded.
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


## Setup

To install the virtualenv:

    virtualenv -p /usr/bin/python3.5 env

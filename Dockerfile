FROM ubuntu:15.10

MAINTAINER Samuel Colvin <s@muelcolvin.com>
ENV DEBIAN_FRONTEND noninteractive

RUN apt-get update -qq
RUN apt-get install apt-utils -qq --yes --force-yes &&\
 apt-get install -qq --yes --force-yes wget gdebi-core python3.5 python3.5-dev python3-pip libpq-dev postgresql-client

# install wkhtmltopdf
RUN wget --quiet http://download.gna.org/wkhtmltopdf/0.12/0.12.2.1/wkhtmltox-0.12.2.1_linux-trusty-amd64.deb -O /tmp/wkhtmltox.deb
RUN apt-get install apt-utils -qq --yes --force-yes &&\
 gdebi --non-interactive /tmp/wkhtmltox.deb

# setup generator
RUN pip3 install --upgrade pip
WORKDIR /src/
ADD requirements.txt /src/requirements.txt
RUN python3.5 /usr/bin/pip3 install -r /src/requirements.txt

ADD gen /src/gen
ADD docker_cmds/ /src/

ENV DOCKER 1
RUN locale-gen en_GB.UTF-8
ENV LANG en_GB.UTF-8
ENV LANGUAGE en_GB:en
ENV LC_ALL en_GB.UTF-8

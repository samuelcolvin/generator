#!/usr/bin/env bash
cd "$(dirname "$0")"
rm -r deps
mkdir deps
cp -r ../../gen deps/
cp -r ../../requirements.txt deps/
docker build -t worker:1 .

#!/usr/bin/env bash
flake8 --max-line-length 120 --exclude */migrations/* src/
flake=$?
echo "flake exit code:  ${flake}"
#jshint -c test_extras/jshint-conf.json gen/static/js/
#jshint=$?
jshint=0
echo "jshint exit code: ${jshint}"
exit $((${jshint} + ${flake}))

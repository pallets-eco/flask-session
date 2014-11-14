#!/bin/bash

$(python -c "import flask" &> /dev/null) || { echo >&2 "flask not found, run 'pip install requirements.txt'"; exit 1; }
type nosetests >/dev/null 2>&1 || { echo >&2 "nosetests not found, run 'pip install -r tests_requirements.txt'"; exit 1; }
type parts/memcached/bin/memcached >/dev/null 2>&1 || { echo >&2 "parts not found, run 'buildout'"; exit 1; }

TMP=$(mktemp -d /tmp/flask_session.XXXXXX)

parts/memcached/bin/memcached -d > /dev/null
pid_memcached=$!

parts/mongodb/bin/mongod --dbpath $TMP > /dev/null &
pid_mongo=$!

parts/redis/bin/redis-server > /dev/null &
pid_redis=$!

nosetests --with-coverage --cover-package=flask_session

kill $pid_memcached $pid_mongo $pid_redis
rm -rf $TMP

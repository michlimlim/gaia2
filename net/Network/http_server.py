#!/usr/bin/env python

import sys
from bottle import route, run

@route('/hello/<name>')
def index(name):
    return 'Hello %s' % name

run(host=sys.argv[1], port=8080)
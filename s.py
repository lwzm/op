#!/usr/bin/env python3

import collections
import threading
import time
import json

import tornado.concurrent
import tornado.ioloop
import tornado.options
import tornado.web
import tornado.gen
import tornado.stack_context
import tornado.httpclient

import x


class Base(tornado.web.RequestHandler):
    def set_default_headers(self):
        self.set_header("Cache-Control", "no-cache")


class Handler(Base):
    def get(self):
        1


application = tornado.web.Application([
    (r"/", Handler),
], static_path="static", template_path="templates", debug=__debug__)


if __name__ == "__main__":
    import tornado.options
    tornado.options.parse_command_line()
    application.listen(1120, xheaders=True)
    tornado.ioloop.IOLoop.instance().start()

import tornado
import tornado.websocket
import tornado.httpserver
import threading
import time
import base64
import sys, os
import gi
gi.require_version('Gst', '1.0')
from gi.repository import Gst, GObject
import json
import signal



class HTTPServer(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")

def post(self):
    if self.get_argument('basic', None) is not None:
        self.write('Basic Query')

    elif self.get_argument('advanced', None) is not None:
        self.write('Advanced Query')
def start_server(cam_app):
    cam_server = tornado.httpserver.HTTPServer(cam_app)
    #key_server = tornado.httpserver.HTTPServer(key_app)
    cam_server.listen(8888)
    #key_server.listen(8889)
    tornado.ioloop.IOLoop.current().start()
if __name__ == "__main__":

    #init_motors()

    cam_app = tornado.web.Application([
        (r'/', HTTPServer),
    ])
    start_server(cam_app)
    time.sleep(1)


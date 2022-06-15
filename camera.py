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

class CamWSHandler(tornado.websocket.WebSocketHandler):
    def open(self):
        global cam_sockets
        cam_sockets.append(self)
        print('new camera connection')

    def on_message(self, message):
        print (message)

    def on_close(self):
        global cam_sockets
        cam_sockets.remove(self)
        print('camera connection closed')

    def check_origin(self, origin):
        return True


def start_server(cam_app):
    cam_server = tornado.httpserver.HTTPServer(cam_app)
    
    cam_server.listen(8888)
    
    tornado.ioloop.IOLoop.current().start()
    
if __name__ == "__main__":

    #init_motors()

    cam_app = tornado.web.Application([
        (r'/ws', CamWSHandler),
        (r'/', HTTPServer),
        (r"/(preview.jpg)", tornado.web.StaticFileHandler, {'path':'./'})       
    ])
    start_server(cam_app)

    time.sleep(1)
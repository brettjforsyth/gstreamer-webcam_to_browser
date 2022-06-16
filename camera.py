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
import RPi.GPIO as GPIO
import subprocess
import shlex
from PIL import Image

cam_sockets = []

led1Pin = 6 
led2Pin = 13 
led3Pin = 19 
led4Pin = 26 

def send_all(msg):
    for ws in cam_sockets:
        ws.write_message(msg)

class HTTPServer(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")
class HTTPServer2(tornado.web.RequestHandler):
    def get(self):
        self.render("files.html")

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
        #print (message)
        if message == 'large':
            print('large capture')
            os.system('sudo libcamera-still -o /home/brett/Documents/gstreamer-webcam_to_browser/preview.jpg --width 640 --height 480 -n --immediate')
        elif message == 'small':
            list = os.listdir('/home/brett/Documents/gstreamer-webcam_to_browser/lores_images') # dir is your directory path
            number_files = len(list)+1
            #os.system('sudo libcamera-still -o /home/brett/Documents/gstreamer-webcam_to_browser/preview.jpg --width 2328 --height 1748 -n -q 50 --autofocus')
            subprocess.run(shlex.split("sudo libcamera-still -o /home/brett/Documents/gstreamer-webcam_to_browser/lores_images/image_"+str(number_files)+".jpg --width 2328 --height 1748 -n -q 50 --autofocus"))
            image = Image.open('/home/brett/Documents/gstreamer-webcam_to_browser/lores_images/image_'+str(number_files)+'.jpg')
            new_image = image.resize((640, 480))
            new_image.save('/home/brett/Documents/gstreamer-webcam_to_browser/preview.jpg')
            new_image = image.resize((160, 120))
            new_image.save('/home/brett/Documents/gstreamer-webcam_to_browser/lores_images/thumbs/image_'+str(number_files)+'.jpg')
            send_all(str('preview captured'))
        elif message == 'capture_raw':
            list = os.listdir('/home/brett/Documents/gstreamer-webcam_to_browser/hires_images') # dir is your directory path
            number_files = len(list)+1        
            #os.system('sudo libcamera-still -o /home/brett/Documents/gstreamer-webcam_to_browser/hires_images/image_'+str(number_files)+'.dng -r -n --autofocus')
            subprocess.run(shlex.split("sudo libcamera-still -o /home/brett/Documents/gstreamer-webcam_to_browser/hires_images/image_"+str(number_files)+".dng -r -n --autofocus"))
            
            send_all(str('raw captured'))
        elif message == 'led_off':
            GPIO.output(led1Pin, GPIO.LOW)
            GPIO.output(led2Pin, GPIO.LOW)
            GPIO.output(led3Pin, GPIO.LOW)
            GPIO.output(led4Pin, GPIO.LOW)
        elif message == 'led_1':
            GPIO.output(led1Pin, GPIO.HIGH)
            GPIO.output(led2Pin, GPIO.LOW)
            GPIO.output(led3Pin, GPIO.LOW)
            GPIO.output(led4Pin, GPIO.LOW)
        elif message == 'led_2':
            GPIO.output(led1Pin, GPIO.HIGH)
            GPIO.output(led2Pin, GPIO.HIGH)
            GPIO.output(led3Pin, GPIO.LOW)
            GPIO.output(led4Pin, GPIO.LOW)
        elif message == 'led_3':
            GPIO.output(led1Pin, GPIO.HIGH)
            GPIO.output(led2Pin, GPIO.HIGH)
            GPIO.output(led3Pin, GPIO.HIGH)
            GPIO.output(led4Pin, GPIO.LOW)
        elif message == 'led_4':
            GPIO.output(led1Pin, GPIO.HIGH)
            GPIO.output(led2Pin, GPIO.HIGH)
            GPIO.output(led3Pin, GPIO.HIGH)
            GPIO.output(led4Pin, GPIO.HIGH)
            
        

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
    GPIO.setmode(GPIO.BCM) # Broadcom pin-numbering scheme
    GPIO.setup(led1Pin, GPIO.OUT) # LED pin set as output
    GPIO.setup(led2Pin, GPIO.OUT) # LED pin set as output
    GPIO.setup(led3Pin, GPIO.OUT) # LED pin set as output
    GPIO.setup(led4Pin, GPIO.OUT) # LED pin set as output
    GPIO.output(led1Pin, GPIO.LOW)
    GPIO.output(led2Pin, GPIO.LOW)
    GPIO.output(led3Pin, GPIO.LOW)
    GPIO.output(led4Pin, GPIO.LOW)

    cam_app = tornado.web.Application([
        (r'/ws', CamWSHandler),
        (r'/', HTTPServer),
        (r'/files', HTTPServer2),
        (r'/lores_images/(.*)', tornado.web.StaticFileHandler, {'path':'/home/brett/Documents/gstreamer-webcam_to_browser/lores_images'}),
         (r'/hires_images/(.*)', tornado.web.StaticFileHandler, {'path':'/home/brett/Documents/gstreamer-webcam_to_browser/hires_images'}),
        (r"/(preview.jpg)", tornado.web.StaticFileHandler, {'path':'./'}),
        (r"/(bulma.min.css)", tornado.web.StaticFileHandler, {'path':'./'})        
    ])
    start_server(cam_app)

    time.sleep(1)
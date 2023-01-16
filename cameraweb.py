import picamera
import io
import logging
import socketserver
from http import server
import threading 
import time


threadactiveflag=True

with open('index.html','r+') as html:
	WPAGE=html.read()
    


def doorStatus(): #outputs  door and lock status to the stream
    while threadactiveflag:
        buff=open('status.txt','r')
        overlaytext=buff.read()
        camera.annotate_background=picamera.Color('black')
        camera.annotate_text=overlaytext
        buff.close()
       

class StreamHandler(server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/index.html': 
            content = WPAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True: #consumer for the frames 
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(server.ThreadingHTTPServer):
    daemon= True
   
    


    
class DataStream(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = threading.Condition()

    def write(self, streambuf):  #producer via start recording method
        if streambuf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(streambuf)

with picamera.PiCamera(resolution='1280x720', framerate=24) as camera:
    output = DataStream()
    camera.start_recording(output, format='mjpeg')
    camera.rotation=180

    threadStat=threading.Thread(target=doorStatus)
    try:
        threadStat.start()
        address = ('', 8080)
        server = StreamingServer(address, StreamHandler)
        server.serve_forever()
    finally:
        threadactiveflag=False
        threadStat.join()
        camera.stop_recording()

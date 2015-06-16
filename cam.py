#
#
#
import io
import picamera
import time
from PIL import Image

stream = io.BytesIO() 

camera = picamera.PiCamera()
camera.resolution = (2592, 1944)
camera.start_preview()
time.sleep(2)
camera.capture(stream, format="jpeg")
stream.seek(0)
image = Image.open(stream)
time.sleep(2)
camera.close()

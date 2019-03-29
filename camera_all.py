#!/usr/bin/env python2.7  
# this file is run using this command: "sudo python camera_all.py"
import RPi.GPIO as GPIO
from subprocess import call  
from datetime import datetime  

from PIL import Image
import time
import ST7735 as TFT
#import Adafruit_GPIO as GPIO
import Adafruit_GPIO.SPI as SPI

WIDTH = 128
HEIGHT = 160
SPEED_HZ = 4000000

# Raspberry Pi configuration.
DC = 24
RST = 25
SPI_PORT = 0
SPI_DEVICE = 0

GPIO.setmode(GPIO.BCM) #we want to reference the GPIO by chip number

GPIO.setup(17, GPIO.IN, pull_up_down=GPIO.PUD_UP) # shutter main switch is on pin 17
GPIO.setup(12, GPIO.IN, pull_up_down=GPIO.PUD_UP) # shutter preview switch is on pin 12 (halfway down)
GPIO.setup(4, GPIO.OUT, initial=GPIO.HIGH) # status LED is on pin 4, turn it on
GPIO.setup(16, GPIO.OUT, initial=GPIO.HIGH) # backlight control for LCD, turn it on (23?)

# Create TFT LCD display class.
disp = TFT.ST7735(
    DC,
    rst=RST,
    spi=SPI.SpiDev(
        SPI_PORT,
        SPI_DEVICE,
        max_speed_hz=SPEED_HZ))

# Initialize display
disp.begin()
disp.clear((0, 0, 0))
disp.display()

print('Drawing logo')
GPIO.output(16, 1)  #turn on backlight
start_time = time.time()
image = Image.open('/home/pi/DLR_logo.bmp')
image = image.resize((WIDTH, HEIGHT))
disp.display(image)

end_time = time.time()
while((end_time - start_time) < 3):
  end_time = time.time()

print('clearing display')
disp.clear((0, 0, 0))
disp.display()
GPIO.output(16, 0)  #turn off backlight


while 1: #loop forever

  GPIO.output(16, 0)  #turn off backlight

  while GPIO.input(17): #wait for the shutter button...
    GPIO.output(16, 0)  #turn off backlight

    # add a way to only show live view with a button or switch to save power. pin 12
    if (GPIO.input(12)==False):
      GPIO.output(16, 1)  #turn on backlight
      command = "raspistill -n -w 160 -h 128 -rot 90 -q 100 -t 50 -o /home/pi/camera/images/liveview.jpg"
      call ([command], shell=True)
      image = Image.open('/home/pi/camera/images/liveview.jpg')
      #image = image.rotate(90).resize((WIDTH, HEIGHT))
      image = image.resize((WIDTH, HEIGHT))
      disp.display(image)
    pass

  print "BUTTON PRESSED"
  GPIO.output(4, 0)  #turn off LED

  i = datetime.now()  #get date & time for filename  
  now = i.strftime('%Y.%m.%d-%H.%M.%S')
  nowsec = int(i.strftime('%S'))

  photo_name = 'pyimg-' + now + '.jpg'  
  command = "raspistill -n -w 3280 -h 2464 -q 100 -t 100 -o /home/pi/camera/images/" + photo_name
  #shoot the photo  
  call ([command], shell=True)
  GPIO.output(4, 1) #turn on LED

  # Load image (thumbnail?)
  print('Loading image...')
  image = Image.open('/home/pi/camera/images/' + photo_name)

  # Resize the image and rotate it so matches the display.
  image = image.rotate(270).resize((WIDTH, HEIGHT))
  #image = image.resize((WIDTH, HEIGHT))
  
  print('Drawing image')
  GPIO.output(16, 1)  #turn on backlight
  start_time = time.time()
  disp.display(image)

  end_time = time.time()
  while((end_time - start_time) < 3):
    end_time = time.time()

  print('clearing display')
  disp.clear((0, 0, 0))
  disp.display()
  GPIO.output(16, 0)  #turn off backlight

  while(GPIO.input(17)==False):
    j = datetime.now()
    jsec = int(j.strftime('%S'))
    holdsec = jsec - nowsec
    if (holdsec >= 3):
      print holdsec
      command = "sync"
      print command
      call ([command], shell=True)
      command = "sudo shutdown -h now"
      print command
      call ([command], shell=True)


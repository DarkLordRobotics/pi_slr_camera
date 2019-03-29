#!/bin/sh
# 'gpio' command requires WiringPi: sudo apt-get install wiringpi

#current_time=$(date "+%Y.%m.%d-%H.%M.%S")
#raspistill -n -w 3280 -h 2464 -q 100 -t 50 -o /home/pi/camera/images/img_$current_time.jpg

# Configurable stuff...
WIDTH=3280    # Image width in pixels
HEIGHT=2464   # Image height in pixels
QUALITY=100   # JPEG image quality (0-100)
DELAY=100      # delay time before taking a picture

HALT=23       # Halt button GPIO pin (other end to GND)
LED=10        # Status LED pin (v2 Pi cam lacks built-in LED)

gpio -g mode  $HALT up  # Initialize GPIO states
gpio -g mode  $LED out
gpio -g write $LED 1

while :  # Forever
do

  currenttime=$(date +%s)
  #echo "CurrentTime : $currenttime"

  # Check for halt button -- hold >= 3 sec
  while [ $(gpio -g read $HALT) -eq 0 ]; 
  do
    if [ $(($(date +%s)-currenttime)) -eq 0 ]; then
      gpio -g write $LED 0
      current_time=$(date "+%Y.%m.%d-%H.%M.%S")
      raspistill -n -w $WIDTH -h $HEIGHT -q $QUALITY -t $DELAY -o /home/pi/camera/images/pimg_$current_time.jpg
      echo "Current Time before: $current_time"
      current_time=$(date "+%Y.%m.%d-%H.%M.%S")
      echo "Current Time after: $current_time"
      gpio -g write $LED 1
    fi

    if [ $(($(date +%s)-currenttime)) -ge 3 ]; then
      gpio -g write $LED 0
      echo "Delay Time : $(($(date +%s)-currenttime))"
      sync
      gpio -g write $LED 1
      sudo shutdown -h now
    fi
  done


done



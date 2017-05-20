#!/bin/sh
#
# loop for detecting gpio button presses
#
# My tinyboy has an orangepi one.
# https://linux-sunxi.org/Xunlong_Orange_Pi_One#Expansion_Port
#
# Pin 39 & 40: GND - PG7
# Pin 5 & 6:   PA11 - GND
#
# Both should work fine for an external switch to connect.
# https://linux-sunxi.org/GPIO
# XX= (position of letter in alphabet - 1) * 32 + pin number
# for PH18 this would be ( 8 - 1) * 32 + 18 = 224 + 18 = 242 (since 'h' is the 8th letter).
#
# G=6 -> PG7 = GPIO 199
# A=0 -> PA11 = GPIO 11
#
# Far end of the connector
# 1=3V3		2=5V
# 3=PA12	4=5V
# 5=PA11	6=GND
# 7=PA6		7=PA13
# ...
#

test -d /sys/class/gpio/gpio11 || echo 11 > /sys/class/gpio/export
sleep 1         # avoid EBUSY
echo in > /sys/class/gpio/gpio11/direction
sleep 1
while true; do
  if [ "$(cat /sys/class/gpio/gpio11/value)" = "0" ]; then
    (cd /root/gcode; /usr/bin/reprint_last)
  fi
  sleep 1
done


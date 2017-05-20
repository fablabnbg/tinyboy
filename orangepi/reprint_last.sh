#! /bin/sh
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

# echo 199 > /sys/class/gpio/export	# does not work. Value always 0.
echo 11  > /sys/class/gpio/export
echo in > /sys/class/gpio/gpio11/direction

while true; do
  if [ "$(cat /sys/class/gpio/gpio11/value)" = "0" ]; then
    logfile=print.log
    filename=$(tail -n1 print.log | cut -f 1 -d ' ')
    lastmin=$(expr $(tail -n1 print.log | cut -f 2 -d ' ') / 60)
    echo "Repprinting: $filename ($lastmin min)"
    sendtinygcode.py $filename
  fi
  sleep 1
done


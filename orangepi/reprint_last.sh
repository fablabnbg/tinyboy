#! /bin/sh
#
logfile=/root/gcode/print.log
filename=$(tail -n1 $logfile | cut -f 1 -d ' ')
lastmin=$(expr $(tail -n1 $logfile | cut -f 2 -d ' ') / 60)
echo "Repprinting: $filename ($lastmin min)"
sendtinygcode.py $filename


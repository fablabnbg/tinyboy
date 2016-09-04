#! /bin/sh
set -x
if [ -z "$*" ]; then 
  rsync -v *.gcode root@tinyboy:gcode
else
  rsync -v "$@" root@tinyboy:gcode
fi

sleep 2
ssh -tv root@tinyboy screen -D -R

#! /bin/sh
set -x
rsync -v *.gcode root@tinyboy:gcode
sleep 2
ssh -tv root@tinyboy screen -D -R

#! /bin/sh
set -x
rsync -v *.gcode root@tinyboy:gcode
ssh -tv root@tinyboy screen -D -R

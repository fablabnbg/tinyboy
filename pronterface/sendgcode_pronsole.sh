#!/bin/sh
#
# sends gcode via pronsole.py or simply connects with pronsole

if [ -n "$*" ]; then
python Printrun/pronterface.py -e connect -e block_until_online -e load "$1" -e print -e emonitor
else
python Printrun/pronterface.py -e connect -e block_until_online -e M114
fi

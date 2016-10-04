#!/bin/sh
#
# sends gcode via pronsole.py or simply connects with pronsole

dir=$(dirname $0)

if [ -n "$*" ]; then
python $dir/Printrun/pronsole.py -e connect -e block_until_online -e load "$1" -e print -e emonitor
else
set -x
python $dir/Printrun/pronsole.py -e connect # -e block_until_online -e M114
fi


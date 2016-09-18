#! /bin/sh
# tinyboy.sh
# This script asumes 
# a) that you have a DNS entry tinyboy and 
# b) your ssh-key in the root-account of that tinyboy machine.
# c) a gcode subdirectory, for uploading files.
#
# This script uploads all *.gcode from the current directory, (or the named *.gcode files) with rsync.
# then opens a remote shell with a screen session. from this shell, you
# can run sendtinygcode.sh with a gcode file of your choice.
# You can log off without interrupting the print job. When you log in with tinyboy.sh again,
# you will be placed in the same screen session, showing you the progress of the last print job.

set -x
if [ -z "$*" ]; then 
  rsync -v *.gcode root@tinyboy:gcode
else
  rsync -v "$@" root@tinyboy:gcode
fi

sleep 2
ssh -tv root@tinyboy screen -D -R

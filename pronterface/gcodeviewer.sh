#!/bin/sh
sudo apt-get install -q -q python-serial python-wxgtk2.8 python-pyglet python-numpy cython python-libxml2 python-gobject python-dbus python-psutil python-cairosvg

if [ ! -d Printrun ]; then
  git clone git@github.com:kliment/Printrun.git
else
  (cd Printrun; git pull)
fi

set -x
cd Printrun 
python testtools/gcodeviewer.py "$@"


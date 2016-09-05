#! /usr/bin/python
#
# sendtinyboy.py -- most simpilistic gcode forwarder for my 3d printer
#
# (C) 2016 juewei@fabmail.org
# distribute under GPLv2.0 or ask.
#
# 2016-06-23, jw -- initial draught.
# 2016-08-14, jw -- fixed upward move to be really relative.
# 2016-09-05, jw -- better exception handling.
#
import sys, re, serial, time


verbose=False

try:
  ser = serial.Serial("/dev/ttyUSB0", 115200, timeout=3, writeTimeout=10000)
except:
  ser = serial.Serial("/dev/ttyUSB1", 115200, timeout=3, writeTimeout=10000)

if len(sys.argv) <= 1:
  ser.write("G21\n");		# ;metric values
  ser.write("G90\n");		# ;absolute positioning
  ser.write("M104 S190.0\n");		# pre-heat extruder
  # ser.write("G28 Z0\n")		# search endstop
  ser.write("G92 Z0\nG1 Z10.0 F2400\n")	# zero z, then move (relative)
  print("move up 10mm")
  sys.exit(0)

errorcount=0
def ser_readline():
  try:
    line = ser.readline()
    errorcount=0
  except Exception as e:
    line = ''
    print "ser.readline() error: " + str(e)
    time.sleep(1)
    errorcount += 1
    if errorcount > 10: 
      raise e
  return line

file = sys.argv[1]
fd = open(file, 'r')
fd.seek(0,2)	# end
total = fd.tell()
if total == 0: total = 1
fd.seek(0,0)
count = 0
tstamp = time.time()
start_tstamp = tstamp

# gobble away initial boiler plate output, if any
seen = ser_readline()
while len(seen):
  print seen
  seen = ser_readline()

while True:
  line = fd.readline()
  count += len(line)
  if line == '': break
  line = re.sub(';.*', '', line)
  line = re.sub('\s*[\n\r]+$', '', line)
  if line == '': continue

  if len(line) > 0:
    if verbose: print "out", line
    line += "\n"
    while len(line):
      n = ser.write(line)
      if n < 0: raise WriteError()
      line = line[n:]

  while True:
    seen = ser_readline()
    if seen[:2] == 'ok':
      if verbose: print seen
      break
    else:
      print seen,
  
  now = time.time()
  if (now > tstamp + 10):
    bps = float(count) / (1 + now - start_tstamp) 
    eta = ''
    elapsed = "%dmin" % (int((now - start_tstamp)/60))
    if (now > start_tstamp + 2*60):	# start eta calc after 2 min
      secs = int(float(total-count)/bps)
      min = int(secs/60)
      eta = "ETA %dmin" % (min)
    print "%.1f %%, %s" % (count * 100. / total, elapsed)
    tstamp = now
    


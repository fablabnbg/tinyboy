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
# 2016-10-01, jw -- tested and fixed error handling in ser_readline()
# 2016-10-14, jw -- est_time_min from cura ;TIME: string
# 2017-05-18, jw -- writing log file.
# 2017-09-03, jw -- loglookup() added.

import sys, re, serial, time

verbose=False

logfile='print.log'

def loglookup(logfile, name):
  pat = re.compile(re.escape(name) + " (\d+)")
  seconds=None
  with open(logfile) as f:
    for line in f:
      m = pat.match(line)
      if m: seconds = int(m.group(1))
  if seconds: print "Last printed duration: %d min\n" % (seconds/60)

ser=None
errorcount=0
def ser_readline():
  global errorcount
  global ser

  try:
    line = ser.readline()
    errorcount=0
  except Exception as e:
    line = ''
    print "ser.readline() error: " + str(e)
    time.sleep(1)
    errorcount += 1
    if errorcount == 5:
      # full re-init: close and open.
      print "ser.readline() re-initializing serial device ..."
      ser.close()
      ser_open()
    if errorcount > 10: 
      raise e
  return line

def ser_open(device=None, baud=115200, timeout=3, writeTimeout=10000):
  global ser

  if device is None:
    devicelist = [ '/dev/ttyUSB0', '/dev/ttyUSB1', '/dev/ttyUSB2', '/dev/ttyUSB3' ]
  else:
    devicelist = [ device ]

  ser = None
  for dev in devicelist:
    try:
      ser = serial.Serial(dev, 115200, timeout=3, writeTimeout=10000)
    except:
      pass
    if ser is not None: break

  if ser is None:
    print("failed to open device: " + str(devicelist))
    sys.exit(0)

  # gobble away initial boiler plate output, if any
  seen = ser_readline()
  if len(seen) == 6 and seen[:4] == 'wait': seen = ''
  while len(seen):
    print "seen: ", seen,
    seen = ser_readline()
    if len(seen) == 6 and seen[:4] == 'wait': seen = ''

def ser_check():
  empty_count = 0
  while True:
    seen = ser_readline()
    if len(seen) == 6 and seen[:4] == 'wait': seen = ''
    if seen[:2] == 'ok':
      if verbose: print seen
      break
    elif seen == '':
      time.sleep(0.1)
      empty_count += 1
      if empty_count > 50:
        break
    else:
      print "check", seen,

ser_open()

if len(sys.argv) <= 1:
  ser.write("G21\n");		# ;metric values
  ser.write("G90\n");		# ;absolute positioning
  ser.write("M104 S190.0\n");		# pre-heat extruder
  # ser.write("G28 Z0\n")		# search endstop
  ser.write("G92 Z0\nG1 Z10.0 F2400\n")	# zero z, then move (relative)
  ser_check()
  print("move up 10mm")
  ser.write("M109 S190.0\n");		# wait for heat
  ser_check()
  ser.close()
  sys.exit(0)


file = sys.argv[1]
fd = open(file, 'r')
fd.seek(0,2)	# end
total = fd.tell()
if total == 0: total = 1
fd.seek(0,0)
count = 0
tstamp = time.time()
start_tstamp = tstamp

loglookup(logfile, file)

open(logfile, 'a').write(file + " -\n")

est_time_min = 0

while True:
  line = fd.readline()
  count += len(line)
  if line == '': break
  m = re.match(';TIME:(\d*)', line)
  if (m):
    est_time_min = int(int(m.group(1))/60.)
    print("Estimated print time: %d min." % est_time_min)
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

  ser_check()

  now = time.time()
  if (now > tstamp + 10):
    bps = float(count) / (1 + now - start_tstamp) 
    eta = ''
    elapsed = "%d min" % (int((now - start_tstamp)/60))
    if (est_time_min): elapsed += " / %d min" % est_time_min
    if (now > start_tstamp + 2*60):	# start eta calc after 2 min
      secs = int(float(total-count)/bps)
      min = int(secs/60)
      eta = "ETA %d min" % (min)
    print "%.1f %%, %s" % (count * 100. / total, elapsed)
    tstamp = now
    
open(logfile, 'a').write(file + " " + str(tstamp-start_tstamp) + "\n")

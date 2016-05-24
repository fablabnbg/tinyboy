#!/usr/bin/python
#
# stl_cut.py -- a simple tool to cut one STL-model into 
#               halves or other portions. This helps a 3D printer
#               to produce larger objects than would fit on the base
#               plate. The printed parts need to be glued together
#               afterwards.
# Example: stl_cut.py candlestick.stl -xyz 50% 
#               applies 3 cuts parallel to the 3 axis to produce 8 files 
#               candlestick_x1_y1_z1.stl to candlestick_x2_y2_z2.svg
# 
#
# -x 50%   writes NAME_x1.svg and NAME_x2.svg
#          where x1 is the part with the lower x coordinates.
# -y -12mm writes out NAME_y1.svg and NAME_y2.svg
#          where NAME_y2.svg is 12mm wide, and NAME_y1.svg has the rest.
# -z 25%+  writes out 4 slices z1, z2, z3, z4, each of equal height.
#
# The combined options -xyz, -xy, -xz, -yz affect all named axis in the
# same way. Starting with x, then y, then z. 
#
# 0.1 jw, building option parser and scaffolding.
# 0.2 jw, cutboxes_*() implementation.
# 0.3 jw, engine selection option added.

import re,os
from argparse import ArgumentParser
import trimesh


__VERSION__ = '0.3'
__AUTHOR__ = 'Juergen Weigert <juewei@fabmail.org>'


def cutboxes_x(bbox, pos):
  # bbox = [[-63.32, -83.48, 0.] [ 63.32, 83.48, 3.00]]
  x1,y1,z1=bbox[0]
  x2,y2,z2=bbox[1]

  v = None
  if pos[-1] == '%': v = (x2-x1)*.01*float(pos[:-1])+x1
  else:              v = float(pos)
  # print "cutboxes_x ", bbox,v

  out = [ 
    trimesh.primitives.Box(box_center =[(v+x1)*.5, (y2+y1)*.5, (z2+z1)*.5], 
                           box_extents=[(v-x1),    (y2-y1),    (z2-z1)]),
    trimesh.primitives.Box(box_center =[(x2+v)*.5, (y2+y1)*.5, (z2+z1)*.5], 
                           box_extents=[(x2-v),    (y2-y1),    (z2-z1)])
    ]

  # print "cutboxes_x out", out[0].bounds, out[1].bounds
  return out


def cutboxes_y(bbox, pos):
  x1,y1,z1=bbox[0]
  x2,y2,z2=bbox[1]

  v = None
  if pos[-1] == '%': v = (y2-y1)*.01*float(pos[:-1])+y1
  else:              v = float(pos)
  # print "cutboxes_y ", bbox,v

  out = [ 
    trimesh.primitives.Box(box_center =[(x2+x1)*.5, (v+y1)*.5, (z2+z1)*.5], 
                           box_extents=[(x2-x1),    (v-y1),    (z2-z1)]),
    trimesh.primitives.Box(box_center =[(x2+x1)*.5, (y2+v)*.5, (z2+z1)*.5], 
                           box_extents=[(x2-x1),    (y2-v),    (z2-z1)])
    ]

  # print "cutboxes_y out", out[0].bounds, out[1].bounds
  return out


def cutboxes_z(bbox, pos):
  x1,y1,z1=bbox[0]
  x2,y2,z2=bbox[1]

  v = None
  if pos[-1] == '%': v = (z2-z1)*.01*float(pos[:-1])+z1
  else:              v = float(pos)
  # print "cutboxes_z ", bbox,v

  out = [ 
    trimesh.primitives.Box(box_center =[(x2+x1)*.5, (y2+y1)*.5, (v+z1)*.5], 
                           box_extents=[(x2-x1),    (y2-y1),    (v-z1)]),
    trimesh.primitives.Box(box_center =[(x2+x1)*.5, (y2+y1)*.5, (z2+v)*.5], 
                           box_extents=[(x2-x1),    (y2-y1),    (z2-v)])
    ]
  # print "cutboxes_z out", out[0].bounds, out[1].bounds

  return out


def do_cut(axis, pos, name, engine):
  done = []
  print "loading "+name+" ..."
  m = trimesh.load_mesh(name)
  m.process()	# basic cleanup
  # print "... done."

  boxl = []
  if axis == 'x': boxl = cutboxes_x(m.bounds, pos)
  if axis == 'y': boxl = cutboxes_y(m.bounds, pos)
  if axis == 'z': boxl = cutboxes_z(m.bounds, pos)

  base,suf = name.rsplit('.', 1)

  for b in range(len(boxl)):
    outname=base+"_"+axis+str(b+1)+"."+suf
    print "cutting "+outname+"..."
    boxl[b].process()	# basic cleanup
    mcut = m.intersection(boxl[b], engine=engine)
    mcut.process()
    print "saving "+outname+" ..."
    trimesh.io.export.export_stl(mcut, open(outname, "wb+"))
    # print "... done."
    done.append(outname)
  return done


def main():
  parser = ArgumentParser(epilog="Version "+__VERSION__+"\n -- Written by "+__AUTHOR__, description="Cut STL objects into pieces. Call without options to open an STL viewer and get the bounding box printed out.")
  parser.add_argument("-x", metavar='XPOS', help="cut at given X-coordinate, parallel to yz plane. Use '%%' with any value for a relative dimension. E.g. '-x 50%%' cuts the object in two equal halves.")
  # Not implemented: Prefix with '-' to measure from the high coordinates downward. Use units '%%', 'mm' or 'cm'. Suffix with '+' to make multiple equally spaced cuts. ")
  parser.add_argument("-y", metavar='YPOS', help="cut at given Y-coordinate")
  parser.add_argument("-z", metavar='ZPOS', help="cut at given Z-coordinate")
  parser.add_argument("-xy", metavar='POS', help="cut into vertical columns")
  parser.add_argument("-xz", metavar='POS', help="cut into horizontal columns")
  parser.add_argument("-yz", metavar='POS', help="cut into horizontal columns (other direction)")
  parser.add_argument("-d", "--xyz", "--dice", metavar='POS', help="cut into equal sided dices ")
  parser.add_argument("-e", "--engine", help="select the CSG engine. Try 'blender' or 'scad' or check 'pydoc trimesh.boolean.intersection' for more valid values. The openSCAD engine may work better for objects with disconnected parts.")
  parser.add_argument("infile", metavar="SVGFILE", help="The SVG input file")

  args = parser.parse_args()      # --help is automatic

  if args.infile is None:
    parser.exit("No input file given")

  cut = { 'x':None, 'y':None, 'z':None }

  if args.xyz is not None: cut['x']=cut['y']=cut['z']=args.xyz
  if args.xy is not None: cut['x']=cut['y']=args.xy
  if args.xz is not None: cut['x']=cut['z']=args.xz
  if args.yz is not None: cut['y']=cut['z']=args.yz
  if args.x is not None: cut['x']=args.x
  if args.y is not None: cut['y']=args.y
  if args.z is not None: cut['z']=args.z

  if cut['x'] is None and cut['y'] is None and cut['z'] is None:
    print "loading "+args.infile+" ..."
    m = trimesh.load_mesh(args.infile)
    print m.bounds
    m.show(block=False)
    print "In the mesh view window, dragging rotates the view, ctl + drag pans, mouse wheel scrolls, 'z' returns to the base view, 'w' toggles wireframe mode, and 'c' toggles backface culling."
    parser.exit('bounding box printed. Specify one of the -x, -y, -z options to cut something')

  svg = [ args.infile ]

  print "x,y,z: ", cut['x'], cut['y'], cut['z']

  for dim in ('x','y','z'):
    if cut[dim] is not None: 
      done = []
      for f in svg:
        done.extend(do_cut(dim, cut[dim], f, args.engine))
        if f != args.infile: 
          print "... removing "+f
          os.remove(f)
      svg = done

  print "files generated: ", svg


if __name__ == "__main__": main()

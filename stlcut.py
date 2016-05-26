#!/usr/bin/python
#
# (C) 2016, Juergen Weigert, juewei@fabmail.org
# Distribute under GPLv2 or ask.
#
# stl_cut.py -- a simple tool to cut one STL-model into
#               halves or other portions. This helps a 3D printer
#               to produce larger objects than would fit on the base
#               plate. The printed parts need to be glued together
#               afterwards.
#
# The openscad script to intersect two STL files is:
#  intersection(){import("/tmp/tmpNfPiKV.STL");import("/tmp/tmp7L8VFI.STL");}
# In case openscad fails, we should retry with a difference() operation.
#
# Requires:
#
# sudo pip install rtree
# sudo pip install trimesh
#
#-----------------------
#
#
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
# -z 25%-  writes only the first slice (z1).
#
# The combined options -xyz, -xy, -xz, -yz affect all named axis in the
# same way. Starting with x, then y, then z.
#
# 0.1 jw, building option parser and scaffolding.
# 0.2 jw, cutboxes_*() implementation.
# 0.3 jw, engine selection option added.
# 0.4 jw, refactored coords_pos_spec() from cutboxes_x,y,z
#         implemented +,- suffixes via range_list()
# 0.5 jw, option --fix added. Not so effective...
#
# TODO:
#         option --support=0.1 
#         Add a thin wall where the cut went. This prevents lose pieces
#         from falling off during print.
#
import re,os
from argparse import ArgumentParser
import trimesh
import rtree	# only needed for fix_normals()


__VERSION__ = '0.5'
__AUTHOR__ = 'Juergen Weigert <juewei@fabmail.org>'


def range_list(x1, x2, v, items):
  if items == '-': return ( (x1, v), )
  if items == '2': return ( (x1, v), (v, x2) )
  d = v - x1
  x = x1
  ret = [ (x, x+d) ]
  while x+d < x2:
    x = x + d
    ret.append( (x, x+d), )
  return ret

def coords_pos_spec(bbox, pos):
  items = '2'
  if pos[-1] == '-':
    pos = pos[:-1]
    items = '-'
  if pos[-1] == '+':
    pos = pos[:-1]
    items = '+'

  perc=False
  if pos[-1] == '%':
    pos = pos[:-1]
    perc = True

  ret = []
  ret.extend(bbox[0])
  ret.extend(bbox[1])
  ret.append(float(pos))
  ret.append(perc)
  ret.append(items)

  return ret



def cutboxes_x(bbox, pos):
  # bbox = [[-63.32, -83.48, 0.] [ 63.32, 83.48, 3.00]]
  x1,y1,z1, x2,y2,z2, v, perc, items = coords_pos_spec(bbox, pos)
  if perc: v = (x2-x1)*.01*v+x1
  # print "cutboxes_x ", bbox,v

  out = []
  for (l,h) in range_list(x1, x2, v, items):
    print 'x range: [%g .. %g]' % (l, h)
    out.append(trimesh.primitives.Box(
        box_center =[(h+l)*.5, (y2+y1)*.5, (z2+z1)*.5],
        box_extents=[(h-l),    (y2-y1),    (z2-z1)]))
    # print "cutboxes_x out", out[-1].bounds
  return out


def cutboxes_y(bbox, pos):
  x1,y1,z1, x2,y2,z2, v, perc, items = coords_pos_spec(bbox, pos)
  if perc: v = (y2-y1)*.01*v+y1
  # print "cutboxes_y ", bbox,v

  out = []
  for (l,h) in range_list(y1, y2, v, items):
    print 'y range: [%g .. %g]' % (l, h)
    out.append(trimesh.primitives.Box(
        box_center =[(x2+x1)*.5, (h+l)*.5, (z2+z1)*.5],
        box_extents=[(x2-x1),    (h-l),    (z2-z1)]))
    # print "cutboxes_y out", out[-1].bounds
  return out


def cutboxes_z(bbox, pos):
  x1,y1,z1, x2,y2,z2, v, perc, items = coords_pos_spec(bbox, pos)
  if perc: v = (z2-z1)*.01*v+z1
  # print "cutboxes_z ", bbox,v

  out = []
  for (l,h) in range_list(z1, z2, v, items):
    print 'z range: [%g .. %g]' % (l, h)
    out.append(trimesh.primitives.Box(
        box_center =[(x2+x1)*.5, (y2+y1)*.5, (h+l)*.5],
        box_extents=[(x2-x1),    (y2-y1),    (h-l)]))
    # print "cutboxes_z out", out[-1].bounds
  return out


def do_cut(axis, pos, name, engine='blender', fix=False):
  done = []
  print "loading "+name+" ..."
  m = trimesh.load_mesh(name)
  print "guess_units: ", m.guess_units()
  m.process()	# basic cleanup
  if fix:
    m.fix_normals()
    print "is watertight: ", m.fill_holes()
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
    if fix:
      mcut.fix_normals()
      print "is watertight: ", m.fill_holes()
      mcut.process()
    print "saving "+outname+" ..."
    trimesh.io.export.export_stl(mcut, open(outname, "wb+"))
    # print "... done."
    done.append(outname)
  return done


def main():
  parser = ArgumentParser(epilog="Version "+__VERSION__+"\n -- Written by "+__AUTHOR__+"\n -- Example (3 parts): stlcut LFS_Elephant.STL -x 33.4%+ -e scad", description="Cut STL objects into pieces. Call without options to open an STL viewer and get the bounding box printed out.")
  parser.add_argument("-x", metavar='XPOS', help="cut at given X-coordinate, parallel to yz plane. Use '%%' with any value for a relative dimension. E.g. '-x 50%%' cuts the object in two equal halves. Suffix with '-' to create only the first part; Suffix with '+' to make multiple equally spaced cuts.")
  # Not implemented: Prefix with '-' to measure from the high coordinates downward. Use units '%%', 'mm' or 'cm'.
  parser.add_argument("-y", metavar='YPOS', help="cut at given Y-coordinate")
  parser.add_argument("-z", metavar='ZPOS', help="cut at given Z-coordinate")
  parser.add_argument("-xy", metavar='POS', help="cut into vertical columns")
  parser.add_argument("-xz", metavar='POS', help="cut into horizontal columns")
  parser.add_argument("-yz", metavar='POS', help="cut into horizontal columns (other direction)")
  parser.add_argument("-d", "--xyz", "--dice", metavar='POS', help="cut into equal sided dices ")
  parser.add_argument("-e", "--engine", help="select the CSG engine. Try 'blender' or 'scad' or check 'pydoc trimesh.boolean.intersection' for more valid values. The openSCAD engine may work better for objects with disconnected parts.")
  parser.add_argument("-f", "--fix", action='store_true', help="try to fix defects in STL: normals, holes, ...")
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
    m.process()
    if args.fix:
      print "is watertight: ", m.fill_holes()
      m.fix_normals()
      m.process()
    print "guess_units: ", m.guess_units()
    print m.bounds
    bb = m.bounding_box			# oriented parallel to the axis
    # bb = m.bounding_box_oriented	# rotated for minimum size, slow!
    for f in bb.facets():
      bb.visual.face_colors[f] = trimesh.visual.rgba([255,255,0,127])
    # FIXME: transparency and color does not work.
    # (m+bb).show(block=False)
    m.show(block=False)

    print "In the mesh view window, dragging rotates the view, ctl + drag pans, mouse wheel scrolls, 'z' returns to the base view, 'w' toggles wireframe mode, and 'c' toggles backface culling."
    parser.exit('bounding box printed. Specify one of the -x, -y, -z options to cut something')

  svg = [ args.infile ]

  print "x,y,z: ", cut['x'], cut['y'], cut['z']

  for dim in ('x','y','z'):
    if cut[dim] is not None:
      done = []
      for f in svg:
        done.extend(do_cut(dim, cut[dim], f, args.engine, args.fix))
        if f != args.infile:
          print "... removing "+f
          os.remove(f)
      svg = done

  print "files generated: ", svg


if __name__ == "__main__": main()

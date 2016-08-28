#!/usr/bin/python
#
# stl-bool-diff.sh -- compute the boolean difference of two stl files.
# similar idea as stlcut, but more flexible.
#
# must use blender as a python interpreter:
# blender --background --python /tmp/stl-bool-diff-02niw.py
#
# 2016-08-21, juewei@fabmail.org -- initial draught.


import os
import sys
import tempfile
import subprocess
from argparse import ArgumentParser

__VERSION__ = '0.1'
__AUTHOR__ = 'Juergen Weigert <juewei@fabmail.org>'


stl_bool_method='DIFFERENCE'

if __name__ == "__main__":
  output_file = 'output.stl'
  parser = ArgumentParser(epilog="Version "+__VERSION__+"\n -- Written by "+__AUTHOR__+"\n ", description="Boolean operation on STL objects: Difference, Intersection, Union.")

  parser.add_argument("-i", "--intersection", action='store_true', help="calculate boolean intersection instead of difference.")
  parser.add_argument("-u", "--union", action='store_true', help="calculate boolean union instead of difference.")
  parser.add_argument("-o", "--output-file", metavar='OUTPUTFILE', help="File to save output to. Default: " + output_file)
  parser.add_argument("infile1", metavar="STLFILE1", help="The first STL input file, (from which second file is cut away)")
  parser.add_argument("infile2", metavar="STLFILE2", help="The second STL input file")
  args = parser.parse_args()      # --help is automatic
  if args.infile1      is None: parser.exit("No input file given")
  if args.infile2      is None: parser.exit("Need two intput files.")
  if args.output_file  is not None: output_file=args.output_file
  if args.intersection: stl_bool_method='INTERSECT'
  if args.union: 	stl_bool_method='UNION'

  fd,script = tempfile.mkstemp(suffix='.py', prefix='stl-bool-diff-')
  os.write(fd, """
import os
import sys
import bpy

def keep_only_first_mesh():
  # different versions of blender sometimes return the wrong mesh
  objects = bpy.context.scene.objects
  if len(objects) > 1:
    objects[-1].select = False
    for other in objects[:-1]:
      other.select = True
    bpy.ops.object.delete()
  objects[-1].select = True

if __name__ == "__main__":

  # Clear scene of default box
  bpy.ops.wm.read_homefile()
  bpy.ops.object.mode_set(mode='OBJECT')
  bpy.ops.object.select_all(action='SELECT')
  bpy.ops.object.delete(use_global=True)

  mesh_pre  = ['""" + args.infile1 + "', '" + args.infile2 + """']
  mesh_post = os.path.abspath('""" + output_file + """')

  # When you add objects to blender, other elements are pushed back
  # by going last to first on the filenames we can preserve the index relation
  for filename in mesh_pre[::-1]:
    bpy.ops.import_mesh.stl(filepath=os.path.abspath(filename))

  mesh  = bpy.context.scene.objects[0]
  for other in bpy.context.scene.objects[1:]:
    mod = mesh.modifiers.new('boolean', 'BOOLEAN') # add boolean modifier 
    mod.object = other
    mod.operation = '""" + stl_bool_method + """'
  
  bpy.ops.object.modifier_apply(modifier = 'boolean')
  keep_only_first_mesh()  
  bpy.ops.export_mesh.stl(filepath = mesh_post, use_mesh_modifiers = True)
""")
  os.close(fd)
  print("output: " + output_file)
  print(" + blender --background --python " + script)
  subprocess.check_call(["blender", "--background", "--python", script])
  os.remove(script)
  print(output_file + " written.")

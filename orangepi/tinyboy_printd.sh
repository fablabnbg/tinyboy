#! /bin/sh
#
# This daemon monitors a directory, and prints all files that change.


find *.gcode -type f 2>/dev/null | xargs md5sum > .known.md5sum
while true; do
  sleep 5
  find *.gcode -type f 2>/dev/null | xargs md5sum > .new.md5sum
  changed=$(diff  .known.md5sum .new.md5sum | tail -1 | awk '{ if ($1 == ">") { print $3 } }')
  mv .new.md5sum .known.md5sum
  if [ -n "$changed" ]; then
	  echo changed: $changed
	  rsync -v $changed root@tinyboy:gcode
	  ssh root@tinyboy "screen -X select 0 || screen -d -m -S printd"
	  sleep 2 
	  ssh -tv root@tinyboy "screen -X stuff 'sendtinygcode $changed\\n'"
  fi
done

#!/bin/bash

## generic discovery of what UDEV allows us to know. The usb VEND:DEV id is not there.
# mkdir -p  /tmp/usbdev/
# o=/tmp/usbdev/info.$(date +%Y%m%d%H%M%S)
# set 2>1 > $o
# echo DEVNAME = $DEVNAME >> $o


lastpart=$(ls -1 $DEVNAME* | sort -r | head -n 1)
mountpoint=$(mktemp -d)
mount $lastpart $mointpoint
outdir=$mountpoint/network/$(date +%Y%m%d%H%M%S)
echo 255 > /sys/class/leds/*red*/brightness

if [ -d $mountpoint/network ]; then
  mkdir -p $outdir
  wpa_cli status > $outdir/wpa_cli-status
  (a=$(wpa_cli status | grep wpa_state ); echo -n "$a "; test "$a" = 'wpa_state=COMPLETED' && wpa_cli status | grep ip_addr || echo) > $outdir/status
  cp /etc/wpa_supplicant/wpa_supplicant.conf $outdir
  cat << EOF > $mountpoint/network/README.txt
$HOSTNAME uses wpa_suppliacant to try join a wireless network.
A usb stick can be used to monitor success or change the configuration.
Whenever a usb stick is inserted, two actions are performed:

a) The current status of the wireless network is written to 
a subdirectory of /network/

b) If present, wpa_supplicant.conf is copied to /etc/wpa_supplicant/wpa_supplicant.conf and network reconfiguration is started.

The red led is on while the stick is mounted read/write. You can safely remove the usb stick as soon as the red led is off again.
EOF

  if [ -f $mountpoint/network/wpa_supplicant.conf ]; then
    set -x
    exec 2>&1 > $outdir/log
    cp $mountpoint/network/wpa_supplicant.conf /etc/wpa_supplicant
    wpa_cli reconfigure
    sleep 2
    wpa_cli status
    sleep 2
    wpa_cli status
    set +x
  fi
fi
umount $mointpoint
rmdir $mointpoint
echo 0 > /sys/class/leds/*red*/brightness

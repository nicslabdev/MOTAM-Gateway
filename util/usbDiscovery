#!/bin/bash
# Bash script for recognise USB connected devices
# Developed for MOTAM Project
# By Manuel Montenegro. 18/09/2017

for sysdevpath in $(find /sys/bus/usb/devices/usb*/ -name dev); do
    (
        syspath="${sysdevpath%/dev}"
        devname="$(udevadm info -q name -p $syspath)"
        [[ "$devname" == "bus/"* ]] && continue
        eval "$(udevadm info -q property --export -p $syspath)"
        [[ -z "$ID_SERIAL" ]] && continue
        echo "$ID_MODEL_ID-/dev/$devname"
    )
done

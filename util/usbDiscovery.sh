#!/bin/bash
# Bash script for recognise USB connected devices
# Developed for MOTAM Project
# By Manuel Montenegro. 17/07/2019

for sysdevpath in $(find /sys/bus/usb/devices/usb*/ -name dev); do
    (
        syspath="${sysdevpath%/dev}"
        devname="$(udevadm info -q name -p $syspath)"
        [[ "$devname" == "bus/"* ]]
        eval "$(udevadm info -q property --export -p $syspath)"
        [[ -z "$ID_SERIAL" ]]
        echo "$ID_MODEL-/dev/$devname"
    )
done

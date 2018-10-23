#!/bin/bash

# Bash script for start S-MOVING demo
# Developed for MOTAM Project
# By Manuel Montenegro. 16/10/2018

cd /home/pi/S-MOVING

socat pty,raw,echo=0,link=/tmp/ttyV0, pty,raw,echo=0,link=/tmp/ttyV1 &
obdsim -g Logger -s obdlog.db -t /tmp/ttyV0 &
python piHud/pihud/TrafficLight.py &
python -m pihud

sudo killall obdsim
sudo killall socat
#!/bin/bash
cd /home/pi/MOTAM
sudo wifi_pruebas/start.sh

zenity --question --text "Conecte el terminal a la red Wifi Direct"

socat pty,raw,echo=0,link=/tmp/ttyV0, pty,raw,echo=0,link=/tmp/ttyV1 &

sudo python util/loadSession3.py

# obdsim -g Logger -s sessions/UMA-5_10_17-Short-WithSensors-v3-copia.db -t /tmp/ttyV0 &


# python -m pihud


# EXIT
sudo killall python
sudo killall obdsim
sudo killall socat
sudo wifi_pruebas/stop.sh
sudo sh -c 'echo "" > /var/lib/misc/udhcpd.leases'
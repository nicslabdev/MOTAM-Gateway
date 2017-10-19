#!/bin/bash
wpa_cli -i wlan0 terminate -B
wpa_cli -i p2p-wlan0-0 terminate -B
cp /home/pi/MOTAM/wifi_pruebas/fi.* /usr/share/dbus-1/system-services/
service networking restart
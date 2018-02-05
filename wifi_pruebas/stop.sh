#!/bin/bash

# Bash script for stop and return to default Wifi connection
# after starting a wifi direct connection
# Developed for MOTAM Project
# By Manuel Montenegro. 02/11/2017



wpa_cli -i wlan0 terminate -B
wpa_cli -i p2p-wlan0-0 terminate -B
sleep 2
wpa_supplicant -i wlan0 -c /etc/wpa_supplicant/wpa_supplicant.conf -B
service networking restart
killall udhcpd

systemctl enable dhcpcd.service

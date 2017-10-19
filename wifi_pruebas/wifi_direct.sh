#!/bin/bash
mv /usr/share/dbus-1/system-services/fi.* .
killall udhcpd
wpa_cli -i wlan0 terminate -B

sleep 0.3

wpa_supplicant -Dnl80211 -iwlan0 -c /home/pi/MOTAM/wifi_pruebas/p2p_supplicant.conf -B
wpa_cli -iwlan0 p2p_group_add
ifconfig p2p-wlan0-0 192.168.1.2

wpa_cli -ip2p-wlan0-0 wps_pin any 12345670
udhcpd /home/pi/MOTAM/wifi_pruebas/udhcpd.conf
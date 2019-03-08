#!/bin/bash

# Bash script for start Wifi Direct connection
# Developed for MOTAM Project
# By Manuel Montenegro. 02/11/2017

# dhcpcd5 interferes with p2p wpa_supplicant from version 6.11.5
systemctl disable dhcpcd.service

wpa_cli -i wlan0 terminate -B
# its necessary a time for finishing the last command
sleep 0.3
# this config file start p2p-wlan0-0 wifi direct interface
wpa_supplicant -i wlan0 -c /home/pi/MOTAM/wifi_pruebas/p2p_supplicant.conf -B
# enable wifi direct properties
wpa_cli -i wlan0 p2p_group_add
# this is the ip for the wifi direct interface
ifconfig p2p-wlan0-0 192.168.0.1
# choose the configuration for security
wpa_cli -i p2p-wlan0-0 wps_pin any 12345670
# start a dhcp server
udhcpd /home/pi/MOTAM/wifi_pruebas/udhcpd.conf

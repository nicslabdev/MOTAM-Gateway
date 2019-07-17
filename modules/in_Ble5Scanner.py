#! /usr/bin/python3

#########################################################
# Python3 module for reading MOTAM BLE5 beacons. It     #
#  stablish a serial connection with nRF52840 dongle.   #
# MOTAM Project https://www.nics.uma.es/projects/motam  #
# Created by Manuel Montenegro.                         #
#########################################################

import serial
import subprocess
import threading
from modules import SensorStore

class Ble5Scanner:

    def __init__ (self, threadStopEvent, beaconsQueue, beaconThreshold):
        self.motamBeaconBle5Id = "5ebe"
        self.threadStopEvent = threadStopEvent                          # Event from main thread in order to stop all threads
        self.beaconsQueue = beaconsQueue
        self.sensorStore = SensorStore.SensorStore()
        self.beaconThreshold = beaconThreshold                          # Seconds after the beacon will be removed from list
        self.scannerPath = None                                         # Path where is connected nRF52840 dongle
        # list of devices connected by USB to Gateway 
        usbDevices = subprocess.check_output('util/usbDiscovery.sh').decode("utf-8").rstrip()
        for line in usbDevices.split('\n'):
            device = line.split('-')
            if device[0] == 'Extended_Advertisements_Scanner' and '/dev/ttyACM' in device[1]:
                self.scannerPath = device[1]

    def run ( self ):
        ble5Thread = None
        if self.scannerPath:
            ser = serial.Serial(self.scannerPath, 115200)

            # start BLE5 scanner in a thread
            ble5Thread = threading.Thread(target=self.scan, args=(ser,))
            ble5Thread.daemon = True
            ble5Thread.start()
            # timer for purging the beacon list (remove old beacons)
            self.purgeStartTimer ()
            # return the thread objects
            return ble5Thread

    def purgeStartTimer ( self ):
        # check if there are beacons to purge every x seconds
        if not self.threadStopEvent.is_set():
            threading.Timer(0.1, self.purgeStartTimer).start()
            try:
                beaconDict = self.sensorStore.purge(self.beaconThreshold)
                self.beaconsQueue.put(beaconDict)
            except ValueError as err:
                pass

    def scan ( self, ser ):
        while not self.threadStopEvent.is_set():
            beaconData = ser.readline().decode("utf-8").rstrip()#[10:]
            # If the received beacon data is signed (1 for valid signature)
            # ToDo: Check if the beacon timestamp is the current time
            if beaconData [0:2] == "1-" and len(beaconData) > 2:
                beaconData2 = beaconData [18:]
                try:
                    beaconDict = self.sensorStore.add(beaconData2)
                    self.beaconsQueue.put(beaconDict)
                except ValueError as err:
                        pass
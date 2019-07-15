#! /usr/bin/python3

#########################################################
# Python3 module for reading MOTAM BLE4 beacons         #
# MOTAM Project https://www.nics.uma.es/projects/motam  #
# Created by Manuel Montenegro.                         #
#########################################################

from bluepy.btle import Scanner, DefaultDelegate
import struct
import threading
import time
from modules import SensorStore

class Ble4Scanner:

    def __init__ (self, threadStopEvent, beaconsQueue, beaconThreshold):
        self.motamBeaconBle4Id = "debe"
        self.beaconScannerThreshold = 0.3
        self.threadStopEvent = threadStopEvent                          # Event from main thread in order to stop all threads
        self.beaconsQueue = beaconsQueue
        self.sensorStore = SensorStore.SensorStore()
        self.beaconThreshold = beaconThreshold                          # Seconds after the beacon will be removed from list

    def run ( self ):
        # start BLE4 scanner in a thread
        ble4Thread = threading.Thread(target=self.scan)
        ble4Thread.daemon = True
        ble4Thread.start()
        # timer for purging the beacon list (remove old beacons)
        self.purgeStartTimer ( )
        # return the thread objects
        return ble4Thread

    def purgeStartTimer ( self ):
        # check if there are beacons to purge every x
        threading.Timer(0.1, self.purgeStartTimer).start()
        try:
            beaconDict = self.sensorStore.purge(self.beaconThreshold)
            self.beaconsQueue.put(beaconDict)
        except ValueError as err:
            pass

    def scan ( self ):
        scanner = Scanner ()
        while not self.threadStopEvent.is_set():
            devices = scanner.scan (self.beaconScannerThreshold)
            for dev in devices:
                # in case advertising packet has some format error, dev.getScanData() return empty list
                if (len(dev.getScanData()) > 0):
                    [adtype, desc, val] = dev.getScanData()[0]
                    # advertising type must be 0xFF (Manufacturer Data) in MOTAM and length larger than 4 bytes
                    if (adtype==0xFF) and (len(val)>=4) and (val[0:4]==self.motamBeaconBle4Id):
                        try:
                            beaconDict = self.sensorStore.add(val[4:])
                            self.beaconsQueue.put(beaconDict)
                        except ValueError as err:
                            pass


# class ScanDelegate(DefaultDelegate):
#     def __init__(self, motamBeaconBle4Id, beaconsQueue, sensorStore):
#         DefaultDelegate.__init__(self)
#         self.motamBeaconBle4Id = motamBeaconBle4Id
#         self.beaconsQueue = beaconsQueue
#         self.sensorStore = sensorStore

#     def handleDiscovery(self, dev, isNewDev, isNewData):
#         for (adtype, desc, val) in dev.getScanData():
#             # advertising type must be 0xFF and length larger than 4 bytes
#             if ( (adtype==0xFF) and (len(val)>=4) ):
#                 if (val[0:4] == self.motamBeaconBle4Id):
#                     try:
#                         beaconDict = self.sensorStore.add(val[4:])
#                         self.beaconsQueue.put(beaconDict)
#                     except ValueError as err:
#                         pass
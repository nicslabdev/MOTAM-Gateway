#! /usr/bin/python3

#########################################################
# Python3 module for reading MOTAM BLE4 beacons         #
# MOTAM Project https://www.nics.uma.es/projects/motam  #
# Created by Manuel Montenegro.                         #
#########################################################

from bluepy.btle import Scanner, DefaultDelegate
from modules import SensorStore
import struct
import threading


# ==== Global variables ====

# MOTAM constants
motamBeaconBle4Id = "debe"
beaconThreshold = 3                                         # Seconds after the beacon will be removed from list

sensorStore = SensorStore.SensorStore()

class Ble4Scanner:

    def __init__ (self, beaconsQueue):
        self.beaconsQueue = beaconsQueue
        self.sensorStore = SensorStore.SensorStore()

    def run ( self ):
        # start BLE4 scanner in a thread
        scanner = Scanner().withDelegate(ScanDelegate())
        ble4Thread = threading.Thread(target=scanner.scan, args=(0, True))
        ble4Thread.start()
        # timer for purging the beacon list (remove old beacons)
        self.purgeStartTimer ( )
        # return the thread objects
        return ble4Thread
    
    def purgeStartTimer ( self ):
        # check if there are beacons to purge every 0.1 s
        threading.Timer(1, self.purgeStartTimer).start()
        try:
            ble4Dict = self.sensorStore.purge(beaconThreshold)
            # send the dict
        except ValueError as err:
            pass



class ScanDelegate(DefaultDelegate):
    def __init__(self):
        DefaultDelegate.__init__(self)

    def handleDiscovery(self, dev, isNewDev, isNewData):
        for (adtype, desc, val) in dev.getScanData():
                # advertising type must be 0xFF and length larger than 4 bytes
                if ( (adtype==0xFF) and (len(val)>=4) ):
                    if (val[0:4] == motamBeaconBle4Id):
                        try:
                            ble4Dict = sensorStore.add(val[4:])
                            # send the dict
                        except ValueError as err:
                            pass
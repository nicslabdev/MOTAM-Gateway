#! /usr/bin/python3

#########################################################
# Python3 module for reading data from GPS receiver and #
# OBDII interface                                       #
# MOTAM Project https://www.nics.uma.es/projects/motam  #
# Created by Manuel Montenegro.                         #
#########################################################

import threading
import subprocess
from gps import *
from modules import SensorStore


class ObdGpsInterface:


    def __init__ (self, threadStopEvent, dataQueue):
        self.threadStopEvent = threadStopEvent                          # Event from main thread in order to stop all threads
        self.dataQueue = dataQueue
        self.gpsPath = None
        self.obdPath = None

        # scan connected USB devices looking for GPS receiver and OBDII interface
        usbDevices = subprocess.check_output('util/usbDiscovery.sh').decode("utf-8").rstrip()
        for line in usbDevices.split('\n'):
            device = line.split('-')
            if device[1] == 'Serial_Controller_D' and '/dev/ttyUSB' in device[2]:
                self.gpsPath = device[2]
            elif device[1] == 'Serial' and '/dev/ttyUSB' in device[2]:
                self.obdPath = device[2]

    def run (self):

        if self.gpsPath == None or self.obdPath == None:
            print ("OBDII interface or GPS receiver is not connected")
            return None

        obdGpsInterface = threading.Thread(target=self.obdGpsReader)
        obdGpsInterface.daemon = True
        obdGpsInterface.start()

        return obdGpsInterface


    def obdGpsReader ( self ):

        # start GPS Daemon
        subprocess.run(["gpsd", self.gpsPath, "-F", "/var/run/gpsd.sock"])
        self.gpsd = gps (mode=WATCH_ENABLE|WATCH_NEWSTYLE)

        while not self.threadStopEvent.is_set():
            report = self.gpsd.next()
            try:
                print (report.lat)
            except:
                print ("no existe")


        print ("fuera!")
        subprocess.run(["killall", "gpsd"])
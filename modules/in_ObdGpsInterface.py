#! /usr/bin/python3

#########################################################
# Python3 module for reading data from GPS receiver and #
# OBDII interface                                       #
# MOTAM Project https://www.nics.uma.es/projects/motam  #
# Created by Manuel Montenegro.                         #
#########################################################

import threading
import subprocess
import time
import datetime
from gps import *
import obd
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

        # start OBD connection
        connection = obd.OBD(portstr=self.obdPath, fast=False)
        cmd = obd.commands.SPEED

        while not self.threadStopEvent.is_set():
            gpsReport = self.gpsd.next()

            # if gps data is received, ask to OBDII for vehicle speed
            obdResponse = connection.query(cmd)

            try:
                # conversion to UNIX timestamp
                gpsTime = calendar.timegm(datetime.datetime.strptime(gpsReport.time, "%Y-%m-%dT%H:%M:%S.%fZ").timetuple())
                # structure for generated JSON
                carData = {"carInfo": {"engineOn":True, "vss":int(obdResponse.value.magnitude), "lat":gpsReport.lat, "lon":gpsReport.lon, "gpsTime":gpsTime, "course":int(gpsReport.track)}}
                
                # put on the queue the data collected
                self.dataQueue.put(carData)

            except Exception as e:
                pass

        # kill gps daemon when thread stops
        subprocess.run(["killall", "gpsd"])
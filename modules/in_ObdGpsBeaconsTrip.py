#! /usr/bin/python3

#########################################################
# Python3 module for loading a saved trip (session) and #
# capture simulated beacons                             #
# MOTAM Project https://www.nics.uma.es/projects/motam  #
# Created by Manuel Montenegro.                         #
#########################################################

import threading
import sqlite3
import queue
import json
import time
from modules import SensorStore

class ObdGpsBeaconsTrip:

    def __init__ (self, threadStopEvent, dataQueue, beaconThreshold, beaconsTripEnabled, obdGpsBeaconsDbFile):

        self.readStep = 1                                               # time lapse between frame transmissions from Gateway to AVATAR in seconds

        self.threadStopEvent = threadStopEvent                          # Event from main thread in order to stop all threads
        self.dataQueue = dataQueue
        self.beaconThreshold = beaconThreshold                          # Seconds after the beacon will be removed from list
        self.beaconsTripEnabled = beaconsTripEnabled
        self.sensorStore = SensorStore.SensorStore()

        self.sessionRoute = "simulation/sessions/"                      # path of session database file
        if obdGpsBeaconsDbFile:
            self.sessionPath = self.sessionRoute+obdGpsBeaconsDbFile
            print (self.sessionPath)
        else:
            self.sessionPath = self.sessionRoute+"UMA-5_10_17-Simulation_Beacons_v3.2.db"

    def run (self):
        obdGpsBeaconsTripThread = threading.Thread(target=self.dbReader)
        obdGpsBeaconsTripThread.daemon = True
        obdGpsBeaconsTripThread.start()

        return obdGpsBeaconsTripThread

    # read simulated session DB and parse it into data units
    def dbReader ( self ):

        while not self.threadStopEvent.is_set():

            # connection to database
            db=sqlite3.connect(self.sessionPath)

            gpsCurs = db.cursor()
            obdCurs = db.cursor()
            
            if self.beaconsTripEnabled:
                beaconsDataCurs = db.cursor()
        
            try:
                gpsCurs.execute("SELECT * FROM gps")
                obdCurs.execute("SELECT * FROM obd")
                if self.beaconsTripEnabled:
                    beaconsDataCurs.execute("SELECT * FROM beacons_data")

                lastTime = None
                sleepNextTime = None
                sleepCurrentTime = None

                if self.beaconsTripEnabled:
                    beacons_dataRow = beaconsDataCurs.fetchone()

                while not self.threadStopEvent.is_set():
                    # collect first row data from gps table
                    gpsRow = gpsCurs.fetchone()
                    # collect first row data from obd table
                    obdRow = gpsCurs.fetchone()

                    # if the end of database table is reached, exit from loop
                    if gpsRow == None or obdRow == None:
                        break

                    # simulation of time taken between each sample from database
                    if sleepNextTime != None:
                        sleepCurrentTime = sleepNextTime
                        sleepNextTime = gpsRow [6]
                        sleepDiff = sleepNextTime - sleepCurrentTime
                        time.sleep(sleepDiff)
                    else:
                        sleepNextTime = gpsRow[6]

                    # get data values from database
                    lat = gpsRow[0]
                    lon = gpsRow[1]
                    course = int(gpsRow[4])
                    gpsTime = int(gpsRow[5])
                    vss = int(obdRow[2])

                    # filter samples by read step: discard samples too close
                    if lastTime is None or (lastTime+self.readStep) <= gpsRow[6]:
                        lastTime = gpsRow[6]
                        # structure for generated JSON
                        carData = {"carInfo": {"engineOn":True, "vss":vss, "lat":lat, "lon":lon, "gpsTime":gpsTime, "course":course}}

                        # put on the queue the data collected
                        self.dataQueue.put(carData)

                        if self.beaconsTripEnabled:
                            # if there is beacon data for this instant of time, add to data 
                            if beacons_dataRow != None and beacons_dataRow[0] <= lastTime:
                                # load JSON data from beacons_data database table
                                sensorData = json.loads (beacons_dataRow[1])

                                # put on the queue the sensor data collected
                                self.dataQueue.put(sensorData)

                                # take the following row
                                beacons_dataRow = beaconsDataCurs.fetchone()

            except sqlite3.DatabaseError:
                print ('Database Error\r\n')

            except queue.Full:
                print('The queue is full\r\n')

            except Exception as error:
                print ("Unknown error\r\n ", error)

            finally:
                # close safely the database
                db.close()
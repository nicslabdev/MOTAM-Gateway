#! /usr/bin/python3

#########################################################
# Python3 module for simulating MOTAM car trip          #
# MOTAM Project https://www.nics.uma.es/projects/motam  #
# Created by Manuel Montenegro.                         #
#########################################################

import sqlite3
import queue
import json

class ObdGpsSim:

    def __init__(self, sessionPath):
        self.sessionPath = sessionPath

    # read simulated session DB and parse it into data units
    def dbReader ( dbReaderThreadStop ):
    
        print("dbReader")
        # print(dbParsedQueue)
        print (sessionPath)

        # connection to database
        db=sqlite3.connect(sessionPath)
        gpsCurs = db.cursor()
        obdCurs = db.cursor()
        beaconsDataCurs = db.cursor()

        try:
            gpsCurs.execute("SELECT * FROM gps")
            obdCurs.execute("SELECT * FROM obd")
            beaconsDataCurs.execute("SELECT * FROM beacons_data")

            lastTime = None

            beacons_dataRow = beaconsDataCurs.fetchone()

            while not dbReaderThreadStop.is_set():
                # collect first row data from gps table
                gpsRow = gpsCurs.fetchone()
                # collect first row data from obd table
                obdRow = gpsCurs.fetchone()

                # if the end of database table is reached, exit from loop
                if gpsRow == None or obdRow == None:
                    break

                # get data values from database
                lat = gpsRow[0]
                lon = gpsRow[1]
                course = int(gpsRow[4])
                gpsTime = int(gpsRow[5])
                vss = int(obdRow[2])

                # filter samples by read step: discard samples too close
                if lastTime is None or (lastTime+readStep) <= gpsRow[6]:
                    lastTime = gpsRow[6]
                    # structure for generated JSON
                    data = {"time":gpsRow[6], "json": {"carInfo": {"engineOn":True, "vss":vss, "lat":lat, "lon":lon, "gpsTime":gpsTime, "course":course}, "sensors": []}}
                    
                    # if there is beacon data for this instant of time, add to data 
                    if beacons_dataRow != None and beacons_dataRow[0] <= lastTime:

                        # load JSON data from beacons_data database table
                        sensorData = json.loads (beacons_dataRow[1])
                        # add simulated sensors data to general data
                        data2 = {"time":gpsRow[6], "json": {"carInfo": {}, "sensors": []}}
                        data2 ["json"]["sensors"] = sensorData["sensors"]
                        dbParsedQueue.put(data2)
                        # take the following row
                        beacons_dataRow = beaconsDataCurs.fetchone()

                    dbParsedQueue.put(data)


        except sqlite3.DatabaseError:
            print ('Database Error\r\n')

        except queue.Full:
            print('The queue is full\r\n')

        except Exception as error:
            print ("Unknown error\r\n ", error)

        finally:
            # close safely the database
            db.close()
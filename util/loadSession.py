###############################################
# Python Script for load OBDII & GPS sessions #
# MOTAM Proyect                               #
# Created by Manuel Montenegro, 16-11-2017    #
###############################################

# This script should be started by nodeJS

import sqlite3
import signal
import time
import sys, json, numpy as np
import threading

class ServiceExit(Exception):
	# this is necessary for interrupt exception
    pass

def main():
	# Register the signal handlers for interrupting the thread
	signal.signal(signal.SIGTERM, service_shutdown)
	signal.signal(signal.SIGINT, service_shutdown)

	# information about sessionPath and device that it has to simulate
	readedData = read_in()
	sessionPath = readedData[0]
	device = readedData[1]

	# executes this while dont receive a terminal signal from Node.JS 
	try:
		# connection to database
		db=sqlite3.connect(sessionPath)
		tripCurs = db.cursor()
		gpsCurs = db.cursor()
		obdCurs = db.cursor()


		for trip in tripCurs.execute("SELECT * FROM trip"):
			start=trip[1]
			end = trip[2]

			nextTime = None

			for gpsRow in gpsCurs.execute("SELECT * FROM gps WHERE time>(?) AND time<(?)",(start,end)):
				# if this is not the first iteration...
				if (nextTime != None):
					currentTime = nextTime
					nextTime = gpsRow[6]

					# time difference between two samples
					diff = nextTime - currentTime

					# take the same sample for speed from obd
					obdCurs.execute("SELECT vss FROM obd WHERE time=(?)",(currentTime,))

					# obtained information from session
					speed = obdCurs.fetchone()[0];
					lat = gpsRow[0]
					lon = gpsRow[1]

					# if you want information of obd...
					if (device == 'obd'):
						
						new_value (speed)

					# if you want information of gps...
					elif (device == 'gps'):

						coord = [lat,lon]
						new_value(coord)


					# sleep the thread: simulating gps signal delay
					time.sleep(diff)

					# ---- only for debug: neccesary to see database read delay
					# print (int(time.strftime("%s"))-tiempoInicio)
					# print (currentTime - startReal)
					# ---------------------------------------------------------

					# sleep the thread: simulating gps signal delay
					

				# if this is the first row, go to second iteration
				else:				
					nextTime = gpsRow[6]
					# ---- only for debug: neccesary to see database read delay
					# startReal = nextTime
					# tiempoInicio = int(time.strftime("%s"))
					# ---------------------------------------------------------
					
		db.close()


	# if receive terminal signal, close the database
	except ServiceExit:
		# close the database
		db.close()


# this function is for reading data from node.JS caller
def read_in():
	# read the data (sessionPath and device) from Node.JS
	lines = sys.stdin.readlines()
	# delete all the \n introduced for separate device and dbpath
	data = [str(lines[0]).replace("\n",""), str(lines[1]).replace("\n","")]
	return data

# this function is called when a new value arrive
def new_value(response):
	print(response)
	sys.stdout.flush()

# this is the interrupt handler. Used when finish the thread (ctrl+c from keyboard)
def service_shutdown(signum, frame):
    raise ServiceExit

# start process 
if __name__ == '__main__':
    main()

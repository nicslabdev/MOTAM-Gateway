#################################################################
# Python Script for load OBD2 sessions & create a server socket #
# MOTAM Proyect                                                 #
# Created by Manuel Montenegro, 26-10-2017                      #
#################################################################

import sqlite3
import signal
import time
import sys, json, numpy as np
import threading
import socket
import json


class ServiceExit(Exception):
	# necessary for interrupt exception
    pass

def main():

	# register the signal handlers for interrupting the thread
	signal.signal(signal.SIGTERM, service_shutdown)
	signal.signal(signal.SIGINT, service_shutdown)

	# path of session database file
	sessionPath = "/home/pi/MOTAM/sessions/UMA-5_10_17.db"
	# ip and port assigned to the gateway (Raspberry Pi)
	gatewayIP = "192.168.1.2"
	gatewayPort = 9999

	# create socket for data transmission
	sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	# prevent "Address already in use" error
	sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
	# asociate the socket with server address
	sock.bind((gatewayIP, gatewayPort))
	# put the socket in server mode and only accept 1 connection
	sock.listen(1)

	print('Waiting connection...')
	# this block the thread until a connection arrives
	sockConnection, clientAddress = sock.accept()


	# executes this while it doesn't receive a terminal signal
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

					# take the same sample from obd
					obdCurs.execute("SELECT * FROM obd WHERE time=(?)",(currentTime,))
					obdRow = obdCurs.fetchone()

					# obtained information from sessions database
					temp = obdRow[0]
					rpm = obdRow[1]
					vss = obdRow[2]
					maf = obdRow[3]
					throttlepos = obdRow[4]
					lat = gpsRow[0]
					lon = gpsRow[1]
					alt = gpsRow[2]
					speed = gpsRow[3]
					course = gpsRow[4]
					gpsTime = gpsRow[5]

					# python list with all obtained data from database
					sData = [temp,rpm,vss,maf,throttlepos,lat,lon,alt,speed,course,gpsTime]

					# send the data through the socket
					jsonSend (sData, sockConnection)

					# sleep the thread: simulating gps signal delay
					time.sleep(diff)					

				# if this is the first row, go to second iteration
				else:				
					nextTime = gpsRow[6]
					

	# if receive terminal signal
	except ServiceExit:
		print("Terminal Signal received")

	# if the other side close the socket...
	except socket.error:
		print("Connection Closed")
		
	finally:
		# close the database
		db.close()
		# close the socket connection
		sockConnection.close()

# encode data to json and send it by socket
def jsonSend(sData, sockConnection):
	data = {"session": [ {"obd": [ {"temp":sData[0]}, {"rpm":sData[1]}, {"vss":sData[2]}, {"maf":sData[3]}, {"throttlepos":sData[4]} ] }, {"gps": [	{"lat":sData[5]}, {"lon":sData[6]}, {"alt":sData[7]}, {"speed":sData[8]}, {"course":sData[9]}, {"gpsTime":sData[10]} ] } ] }
	jsonData = json.dumps(data)
	sockConnection.sendall (jsonData)

# this is the interrupt handler. Used when the thread is finished (ctrl+c from keyboard)
def service_shutdown(signum, frame):
    raise ServiceExit

# start process 
if __name__ == '__main__':
    main()
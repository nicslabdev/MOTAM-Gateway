#! /usr/bin/python

######################################################
# Python Script that simulates OBDII and sensors     #
# MOTAM Project                                      #
# Created by Manuel Montenegro, Sep 18, 2018. V. 1.2 #
######################################################

import sqlite3
import signal
import time
import socket
import select
import ssl
import json
import os
import subprocess


class ServiceExit(Exception):
	# this is necessary for interrupt exception
    pass

def main():

	# register the signal handlers for interrupting the thread
	signal.signal(signal.SIGTERM, service_shutdown)
	signal.signal(signal.SIGINT, service_shutdown)

	# path of session database file
	sessionPath = "/home/pi/MOTAM/simulation/UMA-5_10_17-Simulation.db"
	# ip and port assigned to the gateway (Raspberry Pi)
	gatewayIP = "192.168.0.1"
	# gateway secure port
	gatewaySPort = 4443
	# gateway no secure port: connection without TLS
	gatewayPort = 9999

	db = None
	sSockConnection = None
	sockConnection = None

	# TLS configuration for connection
	try:
		# create the SSL context
		SSLcontext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
		# server certificate and private key (and its key)
		SSLcontext.load_cert_chain(certfile="/home/pi/MOTAM/Certificates/192.168.0.1.crt", keyfile="/home/pi/MOTAM/Certificates/192.168.0.1.key", password = '123456')
		# Certificate Authority
		SSLcontext.load_verify_locations('/home/pi/MOTAM/Certificates/CA.crt')
		# certificates are required from the other side of the socket connection
		SSLcontext.verify_mode = ssl.CERT_REQUIRED

	except ssl.SSLError:
		print('Private key doesn’t match with the certificate')
		exit()

	procStart = subprocess.Popen(['sudo','/home/pi/MOTAM/wifi_pruebas/start.sh'])
	procStart.wait()
	print()

	# executes this while it doesn't receive a terminal signal
	try:
		# create secure socket and no TLS socket for data transmission
		sSock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		# prevent "Address already in use" error
		sSock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
		# asociate the secure socket with server address an port
		sSock.bind((gatewayIP, gatewaySPort))
		sock.bind((gatewayIP, gatewayPort))
		# put the secure socket in server mode and only accept 1 connection
		sSock.listen(1)
		sock.listen(1)
		# list of sockets: secure and no secure
		socketList = [sSock, sock]

		print('Waiting connection...')
		# this block the thread until a connection arrives
		# readSocketList is a list of sockets ready for reading from the gateway
		readSocketList, writeList, exceptionList = select.select(socketList, [], [])

		# if there are more than 1 socket in list, this will only accept the first one
		# if the connection is not secure
		if readSocketList[0] is sock:
			sockConnection, clientAddress = readSocketList[0].accept()
		# if the connection is secure 
		elif readSocketList[0] is sSock:
			sSockConnection, clientAddress = readSocketList[0].accept()
			# sock connection is a TLS wrapping of sSockConnection
			sockConnection = SSLcontext.wrap_socket(sSockConnection, server_side=True)

		# connection to database
		db=sqlite3.connect(sessionPath)
		tripCurs = db.cursor()
		gpsCurs = db.cursor()
		obdCurs = db.cursor()
		beacons_dataCurs = db.cursor()

		while True:

			# Data Base cursor for beacons data table
			beacons_dataCurs.execute("SELECT * FROM beacons_data")
			# take the first beacon data row from table
			beacons_dataRow = beacons_dataCurs.fetchone()

			# everytime that engine stop and start during session saving, new trip is created
			for trip in tripCurs.execute("SELECT * FROM trip"):
				start = trip[1]
				end = trip[2]

				nextTime = None

				for gpsRow in gpsCurs.execute("SELECT * FROM gps WHERE time>=(?) AND time<(?)",(start,end)):
					# if this is not the first iteration...
					if (nextTime != None):
						currentTime = nextTime
						nextTime = gpsRow[6]

						# time difference between two samples
						diff = nextTime - currentTime

						# sleep the thread: simulating gps signal delay
						time.sleep(diff)

						# take the same sample from obd table
						obdCurs.execute("SELECT * FROM obd WHERE time=(?)",(currentTime,))
						obdRow = obdCurs.fetchone()


						# obtained information about OBDII & GPS from sessions database
						vss = int(obdRow[2])
						lat = gpsRow[0]
						lon = gpsRow[1]
						gpsTime = int(gpsRow[5])
						course = int(gpsRow[4])

						# structure for generating JSON
						data = {"carInfo": {"engineOn":True, "vss":vss, "lat":lat, "lon":lon, "gpsTime":gpsTime, "course":course}, "sensors": []}

						# conditions for triggering a new simulated beacon: beacons_dataRow will be None when no more rows lefts
						if ( (beacons_dataRow != None) and (currentTime >= beacons_dataRow[0])):
							
							# load JSON data from beacons_data database table
							sensorData = json.loads (beacons_dataRow[1])
							# add simulated sensors data to general data
							data ["sensors"] = sensorData["sensors"]

							# take the next simulated beacon data
							beacons_dataRow = beacons_dataCurs.fetchone()

						# encode the data to JSON format
						jsonData = json.dumps(data)
						
						# send the json by socket
						sockConnection.sendall (jsonData.encode())						

					else:				
						nextTime = gpsRow[6]


	# if receive terminal signal
	except ServiceExit:
		print("Terminal Signal received")

	# if the other side close the socket...
	except socket.error:
		print("Connection Closed")
		
	finally:
		if (db != None):
			db.close()
		if(sockConnection != None):
			sockConnection.close()
		if (sSockConnection != None):
			sSockConnection.close()
		if (sSock != None):
			sSock.close()
		if (sock != None):
			sock.close()
		
		procStop = subprocess.Popen(['sudo','/home/pi/MOTAM/wifi_pruebas/stop.sh'])
		procStop.wait()


# this is the interrupt handler. Used when the thread is finished (ctrl+c from keyboard)
def service_shutdown(signum, frame):
    raise ServiceExit

# start process 
if __name__ == '__main__':
    main()
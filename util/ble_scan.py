#!/usr/bin python

################################################
# Python Script for scanning MOTAM BLE Devices #
# MOTAM Project                                #
# Created by Manuel Montenegro, 22-11-2017.    #
################################################

from bluepy import btle
import struct
import json
import socket
import math

# timeout for scanner. If 0, scanning won't stop
scan_time = 0.1

# MOTAM constants
motamBeaconId = '\xde\xbe'
trafficSignBeacon = '\x01'
roadStateBeacon = '\x02'
bicycleBeacon = '\x03'

# ip and port assigned to the gateway (Raspberry Pi)
gatewayIP = "192.168.48.213"
# gatewayIP = "192.168.0.1"
gatewayPort = 9999

# Simulated coordenates of the device
currentLat = 36.721853
currentLon =  -4.494418
currentCourse = 0

# max distance (in meters) between sensors and gateway
limitDistance = 1000

# max desviation angle (in degrees) between sensors and gateway
limitCourse = 150


# function that decode an advertising packet from MOTAM BLE device
def processMotamAdvPacket (addr,rssi,advPacket):

	# discretizing rssi from 1 (weak signal) to 4 (strong signal)
	if (rssi > -75):
		strengh = 4
	elif (rssi > -85):
		strengh = 3
	elif(rssi > -95):
		strengh = 2
	else:
		strengh = 1

	# taking data from advertising packet
	latitude = bytearray.fromhex(advPacket[4:12])
	# '<f' is little endian float format
	latitude = struct.unpack('<f', latitude)[0]

	longitude = bytearray.fromhex(advPacket[12:20])
	longitude = struct.unpack('<f', longitude)[0]

	beaconType = bytearray.fromhex(advPacket[20:22])

	if beaconType == trafficSignBeacon:
		# turn bytearray beaconType into int
		beaconType = struct.unpack('<B', beaconType)[0]

		trafficSignId = bytearray.fromhex(advPacket[22:24])
		trafficSignId = struct.unpack('<B', trafficSignId)[0]

		fromDirection = bytearray.fromhex(advPacket[24:28])
		# '<h' is little endian 2 bytes integer format
		fromDirection = struct.unpack('<h', fromDirection)[0]

		toDirection = bytearray.fromhex(advPacket[28:32])
		toDirection = struct.unpack('<h', toDirection)[0]

		beaconData = [trafficSignId,fromDirection,toDirection]

	elif beaconType == roadStateBeacon:
		beaconType = struct.unpack('<B', beaconType)[0]
		roadState = signalId = bytearray.fromhex(advPacket[22:24])
		roadState = struct.unpack('<B', roadState)[0]
		beaconData = [roadState,]

	elif beaconType == bicycleBeacon:
		beaconType = struct.unpack('<B', beaconType)[0]
		bicycleState = signalId = bytearray.fromhex(advPacket[22:24])
		bicycleState = struct.unpack('<B', bicycleState)[0]
		beaconData = [bicycleState,]

	return [addr,strengh,latitude, longitude, beaconType, beaconData]


# take decoded data from advertising packets and turn into JSON format
def encodingToJson (sensorsData):

	data = {}
	data ['sensors'] = []

	for device in sensorsData:
		sensor = {}

		dataSensor = {}
		dataSensor['id'] = device[0]
		dataSensor['strengh'] = device[1]
		dataSensor['lat'] = device[2]
		dataSensor['lon'] = device[3]
		dataSensor['type'] = device[4]
		dataSensor['specificData'] = {}

		beaconData = device[5]
		specificData = {}

		# type of MOTAM sensor
		if ( device[4] == 1 ):
			specificData['trafficSign'] = beaconData[0]
			specificData['fromDir'] = beaconData[1]
			specificData['toDir'] = beaconData[2]
		elif ( device[4] == 2 ):
			specificData['roadState'] = beaconData[0]
		elif ( device[4] == 3 ):
			specificData['bicycleState'] = beaconData[0]

		dataSensor['specificData'] = specificData

		sensor['sensor'] = dataSensor
		data['sensors'].append(sensor)

	return json.dumps (data)


# create a socket for sending JSON packet
def createConnection ():
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

	return sockConnection


# return distance in meters between two GPS coordinates
def haversine(lat1, lon1, lat2, lon2):
    rad=math.pi/180
    dlat=lat2-lat1
    dlon=lon2-lon1
    R=6372.795477598
    a=(math.sin(rad*dlat/2))**2 + math.cos(rad*lat1)*math.cos(rad*lat2)*(math.sin(rad*dlon/2))**2
    distancia=2*R*math.asin(math.sqrt(a))*1000
    return distancia

# return true if the distance to the sensor is less than limitDistance
# and if the course of the gateway match with the sensor fromDirection
def navegationFilter (decodedDataSensor):

	# data from sensor: latitude, longitude and type
	latSensor = decodedDataSensor[2]
	lonSensor = decodedDataSensor[3]
	typeSensor = decodedDataSensor[4]

	# if the distance is less than limit distance...
	if (haversine(latSensor, lonSensor, currentLat, currentLon) < limitDistance):
		# if this is a sensor with from direction...
		if (typeSensor == 1):
			# from direction that applies the sensor
			courseSensor = decodedDataSensor[5][1]

			# considering that if gateway course is between lower and upper range
			# the beacon is not for us
			lowerCourseLimit = ((courseSensor + (limitCourse))%360.0)
			upperCourseLimit = ((courseSensor + (360.0-limitCourse))%360.0)

			if ( lowerCourseLimit < upperCourseLimit ):
				if ( (currentCourse > lowerCourseLimit) and (currentCourse < upperCourseLimit) ):
					return False
				else:
					return True
			else:
				if ( (currentCourse < lowerCourseLimit) and (currentCourse > upperCourseLimit) ):
					return True
				else:
					return False

		else:
			return True
	else:
		return False


def main ():
	try:
		# start the Wifi Direct socket connection
		sock = createConnection()

		scanner = btle.Scanner()
		
		while True:
			# sensorsData store every MOTAM sensor found 
			# during scan_time and their decoded info
			sensorsData = []

			# scan for devices during scan_time seconds
			devices = scanner.scan(scan_time)

			for dev in devices:
				# in case advertising packet has some format error, 
				# dev.getScanData() return empty list
				if (len(dev.getScanData()) > 0):
					[adtype, desc, val] = dev.getScanData()[0]

					# advertising type must be 0xFF (Manufacturer Data) in MOTAM
					# and length is larger than 4 bytes
					if ( (adtype==0xFF) and (len(val)>=4) ):
						# advertising ID must be ID of MOTAM Beacon. 
						# the data format is little endian,
						advId = bytearray.fromhex(val[:4])
						advId = struct.pack('<h', *struct.unpack('>h', advId))

						# if the beacon has the MOTAM beacon identifier
						if (advId == motamBeaconId):
							# decodedDataSensor has all info about 1 MOTAM sensor
							decodedDataSensor =  processMotamAdvPacket(dev.addr, dev.rssi, val)
							print val

							# apply a filter about distance and course of the device
							if (navegationFilter (decodedDataSensor)):
								# sensorsData has all info about every detected MOTAM sensor 
								sensorsData.append(decodedDataSensor)

			jsonData = encodingToJson (sensorsData)

			# send JSON message through socket
			sock.sendall (jsonData)


	except socket.error as e:
		# error type: e.args[0]
		if (e.args[0] != 99):
			sock.close()
		else:
			# error description: e.args[1]
			print "BLE Scan error: %s" % e.args[1]


if __name__ == "__main__":
	main()

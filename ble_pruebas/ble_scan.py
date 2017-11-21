#!/usr/bin/env python

################################################
# Python Script for scanning MOTAM BLE Devices #
# MOTAM Proyect                                #
# Created by Manuel Montenegro, 20-11-2017.    #
################################################

from bluepy import btle
import struct
import json

# timeout for scanner. If 0, scanning won't stop
scan_time = 0.1

# MOTAM constants
motamBeaconId = '\xde\xbe'
trafficSignBeacon = '\x01'
roadStateBeacon = '\x02'
bicycleBeacon = '\x03'

# function that decode an advertising packet from MOTAM BLE device
# return a list with [addr,rssi,latitude, longitude, beaconType,signalId,beaconData]
# where beaconData is a list of data according to beaconType
def processMotamAdvPacket (addr,rssi,advPacket):

	# discretizing rssi from 1 (weak signal) to 4 (strong signal)
	if (rssi > -75):
		strengh = 1
	elif (rssi > -85):
		strengh = 2
	elif(rssi > -95):
		strengh = 3
	else:
		strengh = 4

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

	jsonData = json.dumps (data)

	print jsonData

	decodedJson = json.loads (jsonData)

	# print decodedJson['sensors'][0]['sensor']['specificData']['trafficSign']

	# print decodedJson


def main ():
	scanner = btle.Scanner()

	# while True:

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

				if (advId == motamBeaconId):
					# decodedDataSensor has all info about 1 MOTAM sensor
					decodedDataSensor =  processMotamAdvPacket(dev.addr, dev.rssi, val)
					# sensorsData has all info about every detected MOTAM sensor 
					sensorsData.append(decodedDataSensor)

	encodingToJson (sensorsData)

if __name__ == "__main__":
	main()

# for debugging: print hexadecimal 
# print binascii.hexlify()

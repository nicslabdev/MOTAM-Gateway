###############################################
# Python Script for use OBDII Scanner ELM327  #
# MOTAM Proyect                               #
# Created by Manuel Montenegro, 13-09-2017    #
###############################################

# This script should be started by nodeJS
# Debugging: Uncomment all the print() and sys.stdout.flush() 
# and start this script "sudo python pyOBD_node.py"

import obd
import sys, json, numpy as np
import time
import signal
import threading

obd.logger.setLevel(obd.logging.DEBUG)

time_interval = 1
class ServiceExit(Exception):
    """
    Custom exception which is used to trigger the clean exit
    of all running threads and the main program.
    """
    pass

def main():

	# Register the signal handlers
	signal.signal(signal.SIGTERM, service_shutdown)
	signal.signal(signal.SIGINT, service_shutdown)

	# List with all the serial ports in RPI
	portnames = obd.scan_serial()

	# Debug
	print("Available ports: " + str(portnames))
	sys.stdout.flush()	

	# verify if the some port is connected to a car connected ELM327
	for port in portnames:

		# Debug
	 	print("Trying port: " + str(port))
	 	sys.stdout.flush()

		connection = obd.OBD(port) # create an asynchronous connection
		#connection = obd.OBD('/dev/pts/1')

		print("connection: " + str(connection))
	 	sys.stdout.flush()

		if connection.status() != obd.OBDStatus.NOT_CONNECTED:
			break # Success! Stop searching for serial

	# if no serial port found
	if not portnames:

		# Debug
		print ("\r\n -> No OBD ELM327 connected to car <- \r\n")
		sys.stdout.flush()

		quit()

	# if there are serial port but no ELM327 connected to car
	if connection.status() == obd.OBDStatus.NOT_CONNECTED:

		# Debug
		print ("\r\n -> No OBD ELM327 connected to car <- \r\n")
		sys.stdout.flush()

		quit()

	print ("El puerto es> "+port)
	connection.close()
	time.sleep(1)
	connection2 = obd.Async(portstr=port, fast=False) # create an asynchronous connection
	# connection = obd.Async('/dev/pts/1')

	# keep track of the car's RPM
	connection2.watch(obd.commands.SPEED, callback=new_value)

	try:

		connection2.start()

		while True:
			time.sleep(0.5)

	except ServiceExit:
		connection2.stop();

# this function is called when a new value arrive
def new_value(response):
	time.sleep(time_interval)
	print(response)
	sys.stdout.flush()

def service_shutdown(signum, frame):
    # print('Caught signal %d' % signum)
    raise ServiceExit

# start process 
if __name__ == '__main__':
    main()

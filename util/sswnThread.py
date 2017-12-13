#! /usr/bin/python

###############################################
# Python Script for use OBDII Scanner ELM327  #
# MOTAM Project                               #
# Created by Manuel Montenegro, 04-10-2017    #
###############################################

# This script should be started by nodeJS

import obd
import sys, json, numpy as np
import time
import signal
import threading


time_interval = 1

class ServiceExit(Exception):
	# this is necessary for interrupt exception
    pass

def main():

	# Register the signal handlers for interrupting the thread
	signal.signal(signal.SIGTERM, service_shutdown)
	signal.signal(signal.SIGINT, service_shutdown)

	#read the port from nodejs parent
	port = read_in()

	# if we have a virtual port (socat link), select baudrate to 9600
		# because there are problems relationated with choosing baudrate method
		# and obdsim with a socat link in Python script
	if port=="/tmp/ttyV1":
		connection = obd.Async(portstr=port, baudrate=9600)
	# if we have a actual serial port, connect with it with fast = False,
		# because there are troubles with current ELM327 interface:
		# don't work with fast = True
	else:
		connection = obd.Async(portstr=port, fast=False)
		
	# keep track of the car's SPEED
	connection.watch(obd.commands.SPEED, callback=new_value)

	try:
		connection.start()

		while True:
			# without sleep, the python thread dont let execute the rest of threads
			time.sleep(time_interval)

	except ServiceExit:
		#stop the connection when finish the thread
		connection.stop()

# this function is for reading data from nodeJS caller
def read_in():
	lines = sys.stdin.readlines()
    #Since our input would only be having one line, parse our JSON data from that
	return json.loads(lines[0])

# this function is called when a new value arrive
def new_value(response):
	#sleep the thread because too many responses
	time.sleep(time_interval)
	print(response)
	sys.stdout.flush()

# this is the interrupt handler. Used when finish the thread (ctrl+c from keyboard)
def service_shutdown(signum, frame):
    raise ServiceExit

# start process 
if __name__ == '__main__':
    main()
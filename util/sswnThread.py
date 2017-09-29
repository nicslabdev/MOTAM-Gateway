###############################################
# Python Script for use OBDII Scanner ELM327  #
# MOTAM Proyect                               #
# Created by Manuel Montenegro, 19-09-2017    #
###############################################

# This script should be started by nodeJS
# Debugging: Uncomment all the print() and sys.stdout.flush() 
# and start this script "sudo python sswnThread.py"

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
	
	connection = obd.Async(portstr=port, fast=False) # create an asynchronous connection

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
    # print('Caught signal %d' % signum)
    raise ServiceExit

# start process 
if __name__ == '__main__':
    main()
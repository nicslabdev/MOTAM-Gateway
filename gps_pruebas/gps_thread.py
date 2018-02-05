#!/usr/bin python

################################################
# Python Script for listening GPS receiver     #
# MOTAM Project                                #
# Created by Manuel Montenegro, 23-11-2017.    #
################################################

import os
from gps import *
from time import *
import time
import threading

gpsd = None

class GpsPoller(threading.Thread):
	def __init__(self):
		threading.Thread.__init__(self)
		global gpsd
		# starting the stream of info from GPS receiver
		gpsd = gps(mode=WATCH_ENABLE)
		self.current_value = None
		self.running = True

	def run (self):
		global gpsd
		while gpsd.running:
			# this will continue to loop and grab EACH 
			# set of gpsd info to clear the buffer
			gpsd.next()

def main ():

	# create a thread that is listening GPS receiver
	gpsp = GpsPoller()

	# start the thread
	gpsp.start()
	while True:
		print gpsd.fix.latitude
		time.sleep(1)

if __name__ == '__main__':
	main()
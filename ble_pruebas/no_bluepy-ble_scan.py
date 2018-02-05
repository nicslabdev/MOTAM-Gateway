#!/usr/bin python

#################################################################
# Python Script for scanning MOTAM BLE Devices (WITHOUT BLUEPY) #
# MOTAM Project                                                 #
# Created by Manuel Montenegro, 15-12-2017.                     #
#################################################################

import subprocess
from threading import Thread

import time

# # function that starts the scan of BLE devices
# def scanBLE ():
# 	# duplicates for receiving all broadcast messages, passive for passive scanning
# 	subprocess.check_output(['hcitool','lescan','--duplicates','--passive'])

# # start a thread for scanning BLE devices
# scanThread = Thread (target=scanBLE)
# scanThread.start()


# p = subprocess.Popen(['hcidump', '-R'], stdout=subprocess.PIPE)
p = subprocess.Popen( ['ping','www.google.es','-c','2'], stdout=subprocess.PIPE )

childState = p.poll()
line = ''

while ( childState == None ):

	childState = p.poll()

	if ( len (line) is not 0 ):
		print line

	line = p.stdout.readline().rstrip()

line = p.stdout.readline().rstrip()
if ( len (line) is not 0 ):
	print line

	



	

	# Aqui a veces suelta muchas lineas en blanco porque p.poll() parece que puede ser lento
		# y devuelve None aunque realmente haya terminado el proceso 



	# Hay que encadenar lineas hasta que se encuentre el simbolo >

	# Quizas sea necesario matar el proceso despues: 
	# Popen.send_signal(signal)
	# Sends the signal signal to the child.


print ('Adios')




	


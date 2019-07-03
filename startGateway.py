#! /usr/bin/python3

#########################################################
# Python3 Script that simulates OBDII, GPS and beacons  #
# received data from car on a supposed trip.            #
# MOTAM project: https://www.nics.uma.es/projects/motam #
# Created by Manuel Montenegro, Jul 02, 2019.           #
#########################################################


import time
import argparse
import threading
import sqlite3
import queue
import json
import socket
import ssl

from modules import in_Ble4Scanner
from modules import in_InteractiveScanner
# from modules import motam_simulation as simulation


# ==== Global variables ====

# Version of this script
scriptVersion = 3.0

# path of session database file
sessionRoute = "simulation/sessions/"
sessionPath = sessionRoute+"UMA-5_10_17-Simulation_Beacons_v2.db"

# path of certificate and its key
certRoute = "certs/"
certPath = certRoute+"pasarela_normal.crt"
keyCertPath = certRoute+"pasarela_normal.key"

# path of CA certificate
caCertPath = certRoute+"cacert.crt"

# path of client.log file (will contain the data received from socket)
clientLogPath = "client.log"

# file handler for logging the receiving data from socket
dumpFile = None

# time lapse between frame transmissions from Gateway to AVATAR in seconds
# readStep = 1

# OBD II and GPS data can be loaded from DB or read from hardware interface
simulatedObdGps = True

# Bluetooth beacons can be loaded from DB or read from hardware
simulatedBeacons = True

# Bluetooth 4 beacons can be real (RPi Bluetooth interface)
ble4Beacons = False

# Bluetooth 5 beacons can be real (nRF52840 dongle)
ble5Beacons = False

# BLE interactive beacons generated from terminal in real time
interactiveBeacons = False

# Seconds after the beacon will be removed from list (beacon is not in range)
beaconThreshold = 1

# Coordinates given by terminal of BLE interactive beacons
interactiveBeaconsCoord = None

# Dump client data received from socket to client.log
dump = False

# ip and port assigned to the gateway in AVATAR-Gateway connection
gatewayIP = "192.168.0.1"

# gateway port in AVATAR-Gateway connection
gatewayPort = 4443

# queue where thread will put data (dictionary) from sensors or interactive simulation
beaconsQueue = queue.Queue()


# ==== Main execution ====

def main():
    global sessionPath
    ble4Thread = None
    bleInteractiveThread = None
    receiveFromSocketThread = None

    # threading event used for closing safely the threads when interrupt signal is received
    threadStopEvent = threading.Event()

    # capture command line arguments
    setUpArgParser()

    # create SSL socket for communication with AVATAR
    sock = createSslSocket ()

     # start thread for reading data received from socket (like user image)
    receiveFromSocketThread = threading.Thread(target=receiveFromSocket, args=(threadStopEvent, sock))
    receiveFromSocketThread.daemon = True
    receiveFromSocketThread.start()

    if (simulatedObdGps):
        pass
        # threading event used for closing safely the DataBase when interrupt signal is received
        # dbReaderThreadStop = threading.Event()

        # start database reader and parser thread
        # gpsSim = simulation.GpsSim (sessionPath)
        # dbReaderThread = threading.Thread(target=gpsSim.dbReader, args=(dbReaderThreadStop,))
        # dbReaderThread.start()

    if (ble4Beacons and not simulatedBeacons and not interactiveBeacons ):
        ble4Scanner = in_Ble4Scanner.Ble4Scanner (threadStopEvent, beaconsQueue, beaconThreshold)
        ble4Thread = ble4Scanner.run()

    if (ble5Beacons and not simulatedBeacons and not interactiveBeacons ):
        pass

    if (interactiveBeacons and not simulatedBeacons and not ble4Beacons and not ble5Beacons):
        bleInteractive = in_InteractiveScanner.InteractiveScanner (threadStopEvent, beaconsQueue, beaconThreshold, interactiveBeaconsCoord)
        bleInteractiveThread = bleInteractive.run()

    # start thread that parse and send by socket the collected data
    sendDataToAvatarThread = threading.Thread(target=sendDataToAvatar, args=(threadStopEvent, sock))
    sendDataToAvatarThread.daemon = True
    sendDataToAvatarThread.start()

    try:
        if ble4Thread != None:
            ble4Thread.join()
        if bleInteractiveThread != None:
            bleInteractiveThread.join()
        if sendDataToAvatarThread != None:
            sendDataToAvatarThread.join()
        if receiveFromSocketThread != None:
            receiveFromSocketThread.join()

    # finishing the execution with Ctrl + c 
    except KeyboardInterrupt:
        threadStopEvent.set()
        
    
    # unknown exception from nobody knows where
    except Exception as error:
        print ("\r\nUnknown error\r\n ", error)

# manage command line interface arguments
def setUpArgParser ( ):

    global sessionPath
    global certPath
    global keyCertPath
    global caCertPath
    global gatewayIP
    global simulatedObdGps
    global simulatedBeacons
    global interactiveBeacons
    global interactiveBeaconsCoord
    global ble4Beacons
    global ble5Beacons
    global dump
    global dumpFile
    global clientLogPath

    # description of the script shown in command line
    scriptDescription = 'This is the main script of MOTAM Gateway'

    # initiate the arguments parser
    argParser = argparse.ArgumentParser(description = scriptDescription)

    # command line arguments
    argParser.add_argument("-l", "--load", help="Loads a specific session database. You have to specify the database file. The file must be on session folder. By default, the script loads a saved session trip.")
    argParser.add_argument("-c", "--cert", help="Loads a specific gateway certificate. By default, the script loads certificate for normal vehicle. The certificate file must be on cetificates folder.")
    argParser.add_argument("-C", "--ca", help="Loads a specific certificate of CA. By default, the script loads AVATAR CA. The certificate file must be on certificates folder.")
    argParser.add_argument("-a", "--address", help="MOTAM Gateway IP address. By default, 192.168.0.1", type=str)
    argParser.add_argument("-r", "--real_obd_gps", help="Use OBDII USB interface and GPS receiver instead of simulating their values. It's neccesary to connect OBDII and GPS by USB.", action='store_true')
    argParser.add_argument("-b", "--real_ble4", help="Uses Bluetooth 4 RPi receiver for capturing road beacons", action='store_true')
    argParser.add_argument("-B", "--real_ble5", help="Use nRF52840 dongle for capturing BLE5 beacons.", action='store_true')
    argParser.add_argument("-i", "--interactive", help="Simulate BLE scanner in real time from terminal input. You can use only '--interactive' (default coordinates) '--interactive 36.778 -4.234' ", nargs='*', type=float)
    argParser.add_argument("-d", "--dump", help="Dumps client messages to client.log.", action='store_true')
    argParser.add_argument("-v", "--version", help="Show script version", action="store_true")

    args = argParser.parse_args ()

    if args.load:
        sessionPath = sessionRoute+args.load

    if args.cert:
        certPath = certRoute + args.cert
        keyCertPath = certRoute + args.cert.split('.')[0]+'.key'

    if args.ca:
        caCertPath = certRoute+args.ca

    if args.address:
        gatewayIP = args.address

    if args.real_obd_gps:
        simulatedObdGps = False

    if args.real_ble4:
        simulatedBeacons = False
        ble4Beacons = True

    if args.real_ble5:
        simulatedBeacons = False
        ble5Beacons = True


    if args.interactive is not None and len(args.interactive) in (0,2):
        simulatedBeacons = False
        interactiveBeacons = True
        interactiveBeaconsCoord = args.interactive

    if args.dump:
        # this will start a new thread that will write in a file all the data received from AVATAR
        dump = True
        dumpFile = open(clientLogPath, "w")

    if args.version:
        print ("MOTAM Simulation script version: ", scriptVersion)
        exit()


# create a SSL connection with AVATAR
def createSslSocket ( ):
    # TLS configuration for connection
    try:
        # create the SSL context
        SSLcontext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        # server certificate and private key (and its key)
        SSLcontext.load_cert_chain(certfile=certPath, keyfile=keyCertPath, password = '123456')
        # Certificate Authority
        SSLcontext.load_verify_locations(caCertPath)
        # certificates are required from the other side of the socket connection
        SSLcontext.verify_mode = ssl.CERT_REQUIRED

        # create secure socket for data transmission
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # prevent "Address already in use" error
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # asociate the secure socket with server address an port
        sock.bind((gatewayIP, gatewayPort))
        # put the secure socket in server mode and only accept 1 connection
        sock.listen(1)
        print ("Waiting connection...")
        # socket accepts the connection
        sockConnection, clientAddress = sock.accept()
        # wrap socket with SSL layer
        sslSockConnection = SSLcontext.wrap_socket(sockConnection, server_side=True)

        # print("SSL established. Peer: {}".format(sslSockConnection.getpeercert()))

        return sslSockConnection


    except ssl.SSLError:
        print('Private key doesnt match with the certificate\r\n')
        exit()

    # if the other side close the socket...
    except socket.error:
        print("Connection Closed")
        exit()

    except KeyboardInterrupt:
        exit()


# Receives an image (or other data) from AVATAR by socket and store it 
def receiveFromSocket (threadStopEvent, sock):

    global dumpFile

    # this will stop the execution with keyboard interrupt
    while not threadStopEvent.is_set():
        readFromSocket (sock)

    dumpFile.close()

# Reads data from socket and dumps it if the flag is activated
def readFromSocket (sock):

    global dumpFile
    global dump

    dataRead = sock.recv(1024)

    if dump:
        dumpFile.write (dataRead.decode("utf-8"))
        dumpFile.flush()

    return dataRead




# Read units of data from database session trip and send it to AVATAR
def sendDataToAvatar ( threadStopEvent, sock ):

    dict = None

    # this will stop the execution with keyboard interrupt
    while not threadStopEvent.is_set():

        dataDict = beaconsQueue.get()

        if 'sensors' in dataDict:
            dict = dataDict
            dict ["carInfo"]= {}

        elif 'carInfo' in dataDict:
            dict = dataDict
            dict ["sensors"]= {}

        try:
            # send the data in JSON format
            sock.sendall (json.dumps(dict).encode())

        # if the other side close the socket...
        except socket.error:
            pass

# start script
if __name__ == '__main__':
    main()
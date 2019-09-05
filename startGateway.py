#! /usr/bin/python3

#########################################################
# Python3 Script that simulates OBDII, GPS and beacons  #
# received data from car on a supposed trip.            #
# MOTAM project: https://www.nics.uma.es/projects/motam #
# Created by Manuel Montenegro, Sep 05, 2019.           #
#########################################################


import os
import time
import argparse
import threading
import sqlite3
import queue
import json
import socket
import ssl
import subprocess

from modules import in_Ble4Scanner
from modules import in_Ble5Scanner
from modules import in_InteractiveScanner
from modules import in_ObdGpsBeaconsTrip


# ==== Global variables ====

# Version of this script
scriptVersion = 3.4

# OBD II and GPS data can be loaded from DB
obdGpsTrip = False
# Bluetooth beacons can be loaded from session DB
beaconsTrip = False
# OBD II and GPS is connected: read from hardware interface
realObdGps = False
# Bluetooth 4 beacons can be real (RPi Bluetooth interface)
ble4Beacons = False
# Bluetooth 5 beacons can be real (nRF52840 dongle)
ble5Beacons = False
# BLE interactive beacons generated from terminal in real time
interactiveBeacons = False
# Camera capture of the driver
camera = False
# Dump client data received from socket to client.log
dump = False
# file handler for logging the receiving data from socket
dumpFile = None

# obdGpsBeacons alternative saved session trip passed by arguments
obdGpsBeaconsDb = None
# Coordinates given by terminal of BLE interactive beacons
interactiveBeaconsCoord = None

# path of certificate and its key
certRoute = "certs/"
certPath = certRoute+"pasarela_normal.crt"
keyCertPath = certRoute+"pasarela_normal.key"
# path of CA certificate
caCertPath = certRoute+"cacert.crt"
# path of client.log file (will contain the data received from socket)
clientLogPath = "client.log"
# path of camera shots
shotsRoute = "shots/"

# Seconds after the beacon will be removed from list (beacon is not in range)
beaconThreshold = 1

# default ip and port assigned to the gateway in AVATAR-Gateway connection
gatewayIP = "192.168.0.1"

# default gateway port in AVATAR-Gateway connection
gatewayPort = 4443

# user logged on the system from AVATAR
user = None

# software timer for taking photos every x seconds with RPi camera modules
cameraTimer = None

# User ID and Group ID of Pi user for managging files
uid = 1000
gid = 1000


# ==== Main execution ====

def main():

    ble4Thread = None
    ble5Thread = None
    bleInteractiveThread = None
    receiveFromSocketThread = None
    obdGpsBeaconsTripThread = None

    # threading event used for closing safely the threads when interrupt signal is received
    threadStopEvent = threading.Event()

    # queue where thread will put data (dictionary format) from sensors or car interfaces (or simulation)
    dataQueue = queue.Queue()

    # capture command line arguments
    setUpArgParser()

    if gatewayIP == "192.168.0.1":
        subprocess.run(["wpa_cli", "-i", "p2p-dev-wlan0", "p2p_find"], capture_output=True)
        subprocess.run(["wpa_cli", "-i", "p2p-dev-wlan0", "p2p_group_add"], capture_output=True)
        subprocess.run("wpa_cli -i $(ip -br link | grep -Po 'p2p-wlan0-\d+') wps_pin any 12345670", shell=True, capture_output=True)

    # create SSL socket for communication with AVATAR
    sock = createSslSocket ()

    # start thread for reading data received from socket (like user image)
    if dump:
        receiveFromSocketThread = threading.Thread(target=receiveFromSocket, args=(threadStopEvent, sock))
        receiveFromSocketThread.daemon = True
        receiveFromSocketThread.start()

    if obdGpsTrip:
        obdGpsBeaconsTrip = in_ObdGpsBeaconsTrip.ObdGpsBeaconsTrip (threadStopEvent, dataQueue, beaconThreshold, beaconsTrip, obdGpsBeaconsDb)
        obdGpsBeaconsTripThread = obdGpsBeaconsTrip.run()

    if (ble4Beacons):
        ble4Scanner = in_Ble4Scanner.Ble4Scanner (threadStopEvent, dataQueue, beaconThreshold)
        ble4Thread = ble4Scanner.run()

    if (ble5Beacons):
        ble5Scanner = in_Ble5Scanner.Ble5Scanner (threadStopEvent, dataQueue, beaconThreshold)
        ble5Thread = ble5Scanner.run()

    if (interactiveBeacons):
        bleInteractive = in_InteractiveScanner.InteractiveScanner (threadStopEvent, dataQueue, beaconThreshold, interactiveBeaconsCoord)
        bleInteractiveThread = bleInteractive.run()

    # start thread for taking shots of the driver every x seconds
    if camera:
        path = shotsRoute + user
        filePath = path + "/%d.jpg"

        if not os.path.exists(shotsRoute):
            os.makedirs(shotsRoute, 0o755)
            os.chown(shotsRoute, uid, gid)
        if not os.path.exists(path):
            os.makedirs(path, 0o755)
            os.chown(path, uid, gid)

        # take picture every 30 seconds
        takePictureStartTimer (threadStopEvent, filePath)

    # start thread that parse and send by socket the collected data
    sendDataToAvatarThread = threading.Thread(target=sendDataToAvatar, args=(threadStopEvent, dataQueue, sock))
    sendDataToAvatarThread.daemon = True
    sendDataToAvatarThread.start()

    try:
        if obdGpsBeaconsTripThread != None:
            obdGpsBeaconsTripThread.join()
        if ble4Thread != None:
            ble4Thread.join()
        if ble5Thread != None:
            ble5Thread.join()
        if bleInteractiveThread != None:
            bleInteractiveThread.join()
        if sendDataToAvatarThread != None:
            sendDataToAvatarThread.join()
        if receiveFromSocketThread != None:
            receiveFromSocketThread.join()

    # finishing the execution with Ctrl + c 
    except KeyboardInterrupt:
        threadStopEvent.set()
        if cameraTimer != None:
            cameraTimer.cancel()

    # unknown exception from nobody knows where
    except Exception as error:
        print ("\r\nUnknown error\r\n ", error)

    finally:
        # Close Wifi-Direct connection
        if gatewayIP == "192.168.0.1":
            subprocess.run("wpa_cli -i p2p-dev-wlan0 p2p_group_remove $(ip -br link | grep -Po 'p2p-wlan0-\d+')", shell=True, capture_output=True)


# create a SSL connection with AVATAR
def createSslSocket ( ):

    global user

    # TLS configuration for connection
    try:
        # create the SSL context
        SSLcontext = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
        # server certificate and private key (and its key)
        SSLcontext.load_cert_chain(certfile=certPath, keyfile=keyCertPath, password = '123456')
        # Certificate Authority
        SSLcontext.load_verify_locations(caCertPath)
        # certificates are required from the other side of the socket connection
        SSLcontext.verify_mode = ssl.CERT_NONE
        # SSLcontext.verify_mode = ssl.CERT_REQUIRED
        # check_hostname to True will require certificate
        # SSLcontext.check_hostname = True

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
        print ("Connection accepted!")

        if SSLcontext.verify_mode == ssl.CERT_REQUIRED:
            user = sslSockConnection.getpeercert() ["subject"][0][0][1]
        elif SSLcontext.verify_mode == ssl.CERT_NONE:
            user = 'anonymous'

        print ("Welcome: ", user)

        return sslSockConnection

    except ssl.SSLError as err:
        print (err)
        subprocess.run("wpa_cli -i p2p-dev-wlan0 p2p_group_remove $(ip -br link | grep -Po 'p2p-wlan0-\d+')", shell=True, capture_output=True)
        exit()

    # if the other side close the socket...
    except socket.error:
        print("Connection Closed")
        subprocess.run("wpa_cli -i p2p-dev-wlan0 p2p_group_remove $(ip -br link | grep -Po 'p2p-wlan0-\d+')", shell=True, capture_output=True)
        exit()

    except KeyboardInterrupt:
        subprocess.run("wpa_cli -i p2p-dev-wlan0 p2p_group_remove $(ip -br link | grep -Po 'p2p-wlan0-\d+')", shell=True, capture_output=True)
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
        # dumpFile.write(str(time.time()))
        # dumpFile.write ("\r\n")
        dumpFile.write (dataRead.decode("utf-8"))
        # dumpFile.write ("\r\n\r\n\r\n")
        dumpFile.flush()

    return dataRead

def takePictureStartTimer (threadStopEvent, filePath):

    global cameraTimer

    if not threadStopEvent.is_set():
        # take picture every 30 sec
        cameraTimer = threading.Timer(30, takePictureStartTimer, [threadStopEvent, filePath])
        cameraTimer.start()
        subprocess.run(["raspistill", "-rot", "180", "-t", "500", "-ts", "-o", filePath, "-n"])


# Read units of data from database session trip and send it to AVATAR
def sendDataToAvatar ( threadStopEvent, dataQueue, sock ):

    dict = None

    # this will stop the execution with keyboard interrupt
    while not threadStopEvent.is_set():

        dataDict = dataQueue.get()

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


# manage command line interface arguments
def setUpArgParser ( ):

    global certPath
    global keyCertPath
    global caCertPath
    global gatewayIP
    global obdGpsTrip
    global beaconsTrip
    global obdGpsBeaconsDb
    global interactiveBeacons
    global interactiveBeaconsCoord
    global ble4Beacons
    global ble5Beacons
    global dump
    global dumpFile
    global clientLogPath
    global camera

    # description of the script shown in command line
    scriptDescription = 'This is the main script of MOTAM Gateway. By default, this starts a Wifi Direct connection'

    # initiate the arguments parser
    argParser = argparse.ArgumentParser(description = scriptDescription)

    # command line arguments
    argParser.add_argument("-l", "--loadCarTrip", help="Loads a specific session database. This will simulate only OBDII and GPS data. You can use default saved session trip database or indicate the name of another one placed in sessions folder: '--load' or '--load Session.db'", nargs='?', type=str, const='no_path')
    argParser.add_argument("-L", "--loadBeaconsTrip", help="This arguments must be indicated together with '--loadCarTrip'. This activates the simulated beacons from session database.", action='store_true')
    argParser.add_argument("-c", "--cert", help="Loads a specific gateway certificate. By default, the script loads certificate for normal vehicle. The certificate file must be on cetificates folder.")
    argParser.add_argument("-C", "--ca", help="Loads a specific certificate of CA. By default, the script loads AVATAR CA. The certificate file must be on certificates folder.")
    argParser.add_argument("-a", "--address", help="Disables Wifi-Direct and open socket on selected IP ", type=str)
    argParser.add_argument("-r", "--real_obd_gps", help="Uses OBDII USB interface and GPS receiver instead of simulating their values. It's neccesary to connect OBDII and GPS by USB.", action='store_true')
    argParser.add_argument("-b", "--real_ble4", help="Uses Bluetooth 4 RPi receiver for capturing road beacons", action='store_true')
    argParser.add_argument("-B", "--real_ble5", help="Uses nRF52840 dongle for capturing BLE5 beacons.", action='store_true')
    argParser.add_argument("-i", "--interactive", help="Simulates BLE scanner in real time from terminal input. You can use only '--interactive' (default coordinates) '--interactive 36.778 -4.234' ", nargs='*', type=float)
    argParser.add_argument("-d", "--dump", help="Dumps client messages to client.log.", action='store_true')
    argParser.add_argument("-s", "--shots", help="Starts camera and begins taking pictures of the driver", action="store_true")
    argParser.add_argument("-v", "--version", help="Shows script version", action="store_true")

    args = argParser.parse_args ()

    if args.loadCarTrip:
        obdGpsTrip = True
        if args.loadCarTrip != 'no_path':
            obdGpsBeaconsDb = args.loadCarTrip
        if args.loadBeaconsTrip:
            beaconsTrip = True

    if args.cert:
        certPath = certRoute + args.cert
        keyCertPath = certRoute + args.cert.split('.')[0]+'.key'

    if args.ca:
        caCertPath = certRoute+args.ca

    if args.address:
        gatewayIP = args.address

    if args.real_obd_gps:
        pass

    if args.real_ble4:
        ble4Beacons = True

    if args.real_ble5:
        ble5Beacons = True

    if args.interactive is not None and len(args.interactive) in (0,2):
        interactiveBeacons = True
        interactiveBeaconsCoord = args.interactive

    if args.dump:
        # this will start a new thread that will write in a file all the data received from AVATAR
        dump = True
        dumpFile = open(clientLogPath, "w")

    if args.shots:
        camera = True

    if args.version:
        print ("MOTAM Simulation script version: ", scriptVersion)
        exit()

# start script
if __name__ == '__main__':
    main()
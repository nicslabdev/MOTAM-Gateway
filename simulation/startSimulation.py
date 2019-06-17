#! /usr/bin/python3

#########################################################
# Python3 Script that simulates OBDII, GPS and beacons  #
# received data from car on a supposed trip.            #
# MOTAM project: https://www.nics.uma.es/projects/motam #
# Created by Manuel Montenegro, Jun 17, 2019.    V. 2.2 #
#########################################################


import time
import argparse
import threading
import sqlite3
import queue
import json
import socket
import ssl


# ==== Global variables ====

# Version of this script
scriptVersion = 2.2

# path of session database file
sessionRoute = "sessions/"
sessionPath = sessionRoute+"UMA-5_10_17-Simulation_Beacons_v2.db"

# path of certificate and its key
certRoute = "../certs/"
certPath = certRoute+"pasarela_normal.crt"
keyCertPath = certRoute+"pasarela_normal.key"

# path of CA certificate
caCertPath = certRoute+"cacert.crt"

# time lapse between frame transmissions from Gateway to AVATAR in seconds
readStep = 1

# OBD II and GPS data can be loaded from DB or read from hardware interface
simulatedObdGps = True

# Bluetooth 5 beacons can be loaded from DB or read from hardware
simulatedBeacons = True

# ip and port assigned to the gateway in AVATAR-Gateway connection
gatewayIP = "192.168.0.1"

# gateway port in AVATAR-Gateway connection
gatewayPort = 4443

# queue where dbReader thread will put parsed simulation database data
dbParsedQueue = queue.Queue()


# ==== Main execution ====

def main():

    # capture command line arguments
    setUpArgParser()

    # create SSL socket for communication with AVATAR
    sock = createSslSocket ()

    # threading event used for closing safely the DataBase when interrupt signal is received
    dbReaderThreadStop = threading.Event()
    # start database reader and parser thread
    dbReaderThread = threading.Thread(target=dbReader, args=(dbReaderThreadStop,))
    dbReaderThread.start()

    # threading event used for closing safely the socket connection when interrupt signal is received
    sendDataThreadStop = threading.Event()
    # start database reader and parser thread
    sendDataThread = threading.Thread(target=sendData, args=(dbReaderThreadStop,sock))
    sendDataThread.start()

    try:
        dbReaderThread.join()
        sendDataThread.join()

    # finishing the execution with Ctrl + c 
    except KeyboardInterrupt:
        # send close event in order to safely close DB and socket
        dbReaderThreadStop.set()
        sendDataThreadStop.set()
    
    # unknown exception from nobody know where
    except Exception as error:
        print ("\r\nUnknown error\r\n ", error)


# manage command line interface arguments
def setUpArgParser ( ):

    global sessionPath
    global certPath
    global keyCertPath
    global caCertPath
    global readStep
    global gatewayIP

    # description of the script shown in command line
    scriptDescription = 'This script runs a car trip simulation. The purpose is testing MOTAM subsystems'

    # initiate the arguments parser
    argParser = argparse.ArgumentParser(description = scriptDescription)

    # command line arguments
    argParser.add_argument("-l", "--session", help="Loads a specific session database. You have to specify the database file. The file must be on session folder. By default, the script loads a saved session trip.")
    argParser.add_argument("-c", "--cert", help="Loads a specific gateway certificate. By default, the script loads certificate for normal vehicle. The certificate file must be on cetificates folder.")
    argParser.add_argument("-a", "--ca", help="Loads a specific certificate of CA. By default, the script loads AVATAR CA. The certificate file must be on certificates folder.")
    argParser.add_argument("-s", "--step", help="Frequency of frame transmissions from Gateway to AVATAR in seconds. By default, "+str(readStep)+" seconds.", type=float)
    argParser.add_argument("-d", "--address", help="MOTAM Gateway IP address. By default, 192.168.0.1", type=str)
    # argParser.add_argument("-r", "--real_obd_gps", help="Use OBDII USB interface and GPS receiver instead of simulating their values. It's neccesary to connect OBDII and GPS by USB. By default, the script loads this data from session trip.", action='store_true')
    # argParser.add_argument("-b", "--real_beacons", help="Use nRF52840 dongle for capturing road beacons instead of simulating its values. By default, the script loads this data from session trip.", action='store_true')
    argParser.add_argument("-v", "--version", help="Show script version", action="store_true")

    args = argParser.parse_args ()

    if args.session:
        sessionPath = sessionRoute+args.session

    if args.cert:
        certPath = certRoute + args.cert
        keyCertPath = certRoute + args.cert.split('.')[0]+'.key'

    if args.ca:
        caCertPath = certRoute+args.ca

    if args.step:
        readStep = args.step

    if args.address:
        gatewayIP = args.address

    # if args.real_obd_gps:
    #     global simulatedObdGps
    #     simulatedObdGps = False

    # if args.real_beacons:
    #     global simulatedBeacons
    #     simulatedBeacons = False

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


# read simulated session DB and parse it into data units
def dbReader ( dbReaderThreadStop ):

    global readStep

    # connection to database
    db=sqlite3.connect(sessionPath)
    gpsCurs = db.cursor()
    obdCurs = db.cursor()
    beaconsDataCurs = db.cursor()

    try:
        gpsCurs.execute("SELECT * FROM gps")
        obdCurs.execute("SELECT * FROM obd")
        beaconsDataCurs.execute("SELECT * FROM beacons_data")

        lastTime = None

        beacons_dataRow = beaconsDataCurs.fetchone()

        while not dbReaderThreadStop.is_set():
            # collect first row data from gps table
            gpsRow = gpsCurs.fetchone()
            # collect first row data from obd table
            obdRow = gpsCurs.fetchone()

            # if the end of database table is reached, exit from loop
            if gpsRow == None or obdRow == None:
                break

            # get data values from database
            lat = gpsRow[0]
            lon = gpsRow[1]
            course = int(gpsRow[4])
            gpsTime = int(gpsRow[5])
            vss = int(obdRow[2])

            # filter samples by read step: discard samples too close
            if lastTime is None or (lastTime+readStep) <= gpsRow[6]:
                lastTime = gpsRow[6]
                # structure for generated JSON
                data = {"time":gpsRow[6], "json": {"carInfo": {"engineOn":True, "vss":vss, "lat":lat, "lon":lon, "gpsTime":gpsTime, "course":course}, "sensors": []}}
                
                # if there is beacon data for this instant of time, add to data 
                if beacons_dataRow != None and beacons_dataRow[0] <= lastTime:

                    # load JSON data from beacons_data database table
                    sensorData = json.loads (beacons_dataRow[1])
                    # add simulated sensors data to general data
                    data2 = {"time":gpsRow[6], "json": {"carInfo": {}, "sensors": []}}
                    data2 ["json"]["sensors"] = sensorData["sensors"]
                    dbParsedQueue.put(data2)
                    # take the following row
                    beacons_dataRow = beaconsDataCurs.fetchone()

                dbParsedQueue.put(data)


    except sqlite3.DatabaseError:
        print ('Database Error\r\n')

    except queue.Full:
        print('The queue is full\r\n')

    except Exception as error:
        print ("Unknown error\r\n ", error)

    finally:
        # close safely the database
        db.close()


# Read units of data from database session trip and send it to AVATAR
def sendData ( sendDataThreadStop, sock ):

    # take the first data unit from the queue
    data = dbParsedQueue.get()

    # this variables will control the sample frequency
    currentSimulatedTime = None
    lastSimulatedTime = data["time"]
    
    try:
        # send the first json
        sock.sendall (json.dumps(data["json"]).encode())

        # this will stop the execution with keyboard interrupt
        while not sendDataThreadStop.is_set():
            # if this is the first iteration...
            if currentSimulatedTime is None:
                # take the data unit from the queue
                data = dbParsedQueue.get()
                currentSimulatedTime = data["time"]
            
            # if this isn't the first iteration
            else:
                time.sleep(currentSimulatedTime-lastSimulatedTime)

                # send the next json
                sock.sendall (json.dumps(data["json"]).encode())
                
                try:
                    # take the data unit from the queue
                    data = dbParsedQueue.get(block=False)
                    lastSimulatedTime = currentSimulatedTime
                    currentSimulatedTime = data["time"]
                    
                except queue.Empty:
                    pass

    # if the other side close the socket...
    except socket.error:
        pass


# start script
if __name__ == '__main__':
    main()
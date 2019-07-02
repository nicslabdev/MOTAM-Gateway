#! /usr/bin/python3

#########################################################
# Python3 module for simulating BLE scanner (both BLE4  #
# and BLE5) in real time.                               #
# MOTAM Project https://www.nics.uma.es/projects/motam  #
# Created by Manuel Montenegro.                         #
#########################################################

import threading
import struct
from modules import SensorStore

class InteractiveScanner:

    def __init__ (self, threadStopEvent, beaconsQueue, coordinates):
        self.threadStopEvent = threadStopEvent                          # Event from main thread in order to stop all threads
        self.beaconsQueue = beaconsQueue
        self.sensorStore = SensorStore.SensorStore()
        self.beaconThreshold = 3                                        # Seconds after the beacon will be removed from list
        
        self.dataBeaconSamples = {
            1: ("Sillita sentado sin abrochar", "0001000200030004040100"),
            2: ("Sillita sentado abrochado", "0001000200030004040101"),
            3: ("Sillita sin sentar no abrochado", "0001000200030004040000"),
            4: ("Semáforo normal rojo", "4212DDEDC09004EC01000118000A"),
            5: ("Semáforo normal ambar", "4212DDEDC09004EC01010118000A"),
            6: ("Semáforo normal verde", "4212DDEDC09004EC01020118000A"),
            7: ("Carretera seca", "4212DD69C08FF4690201"),
            8: ("Carretera mojada", "4212DD69C08FF4690202"),
            9: ("Carretera nieve", "4212DD69C08FF4690203"),
            10: ("Bicicleta en movimiento", "00010002000300040302"),
            11: ("Bicicleta accidentada", "00010002000300040303")
            # 9: {"Sillita sentado sin abrochar": "01"},
            # 10: {"Sillita sentado abrochado": "01"},
            # 11: {"Sillita sin sentar no abrochado": "01"},
            # 12: {"Semáforo inteligente rojo 10 segundos": "01"},
            # 13: {"Semáforo inteligente verde 3 segundos": "01"},
            # 14: {"infoPanel Incendio": "01"},
            # 15: {"infoPanel Carrera ciclista": "01"},
            # 16: {"Peatón cerca": "01"},
            # 17: {"Vehículo lento": "01"},
            # 18: {"Vehículo de emergencia": "01"}
        }

        # Check if new coordinates has been given
        if len(coordinates) is 2:
            newLat = str(hex(struct.unpack('<I', struct.pack('<f', coordinates[0]))[0])).split('x')[1].upper()
            newLon = str(hex(struct.unpack('<I', struct.pack('<f', coordinates[1]))[0])).split('x')[1].upper()

            for element in self.dataBeaconSamples:
                oldLat = self.dataBeaconSamples[element][1][0:8]
                oldLon = self.dataBeaconSamples[element][1][8:16]
                newBeaconData = newLat + newLon + self.dataBeaconSamples[element][1][16:]
                self.dataBeaconSamples[element] = (self.dataBeaconSamples[element][0],newBeaconData)

    def run (self):
        interactiveThread = threading.Thread(target=self.terminalInputOutput)
        interactiveThread.start()
        self.purgeStartTimer ( )
        return interactiveThread

    def terminalInputOutput (self):
        while not self.threadStopEvent.is_set():
            print ("List of beacon samples:")
            print ("ID - Beacon frame - Name\r\n")
            for dataBeaconIndex in self.dataBeaconSamples:
                print (" ", dataBeaconIndex, "-", self.dataBeaconSamples[dataBeaconIndex][1], "-", self.dataBeaconSamples[dataBeaconIndex][0] )
            try:
                index = int(input("\r\nSelect the beacon sample ID: "))
                if index > 0 and index <= len(self.dataBeaconSamples):
                    beaconDict = self.sensorStore.add(self.dataBeaconSamples[index][1])
                    self.beaconsQueue.put(beaconDict)
                else:
                    print ("\r\n  :Invalid value\r\n")

            except ValueError as err:
                pass


    def purgeStartTimer ( self ):
        # check if there are beacons to purge every x seconds
        threading.Timer(1, self.purgeStartTimer).start()
        try:
            beaconDict = self.sensorStore.purge(self.beaconThreshold)
            self.beaconsQueue.put(beaconDict)
        except ValueError as err:
            pass



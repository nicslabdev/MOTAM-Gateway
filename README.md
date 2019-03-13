# MOTAM - Gateway

MOTAM - Gateway repository contains the applications of the vehicle's gateway on MOTAM platform.

The gateway collects all the road state and vehicles information from MOTAM infraestructure. This data is analized, parsed and send by a secure connection to AVATAR Android application.

Another MOTAM related repositories and more info about MOTAM project can be found on:
> [**MOTAM project website by NICS.**](https://www.nics.uma.es/projects/motam)

## Hardware list
MOTAM Gateway is supported by Raspberry Pi 3 Model B. 
Several peripherals are attached to Raspberry Pi in order to collect different kind of data from the own car, near vehicles and Road Side Units.
The peripherals are listed below:

 - Raspberry Pi 7" Touch Display.
 - ELM327 OBD II Interface.
 - BU-353S4 USB GPS Receiver from GlobalSat.
 - UPS PIco HV3.0B from PiModules.
 - nRF52840 dongle from NordicSemiconductor.

![MOTAM-Gateway](https://i.imgur.com/XAnsNOE.jpg)

## Simulation
MOTAM-Gateway can simulate a car trip in order to send simulated data to AVATAR app. 
It's possible to select the kind of data that is simulated and what data come from real sources. This may be useful for development and testing purpouses.
How-to can be found on simulation folder.

## Bluetooth 5 Beacon Scanner
The firmware of nRF52840 dongle Beacon Scanner can be found on its repository.

> [**MOTAM Scanner repository on GitHub.**](https://github.com/nicslabdev/MOTAM-Scanner)

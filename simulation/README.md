# Gateway simulation #

Here you can find a preloaded simulation of a car trip. The information is sent by a Wifi Direct socket in JSON format.

This Python script starts the Wifi Direct connection, so it isn't necessary to run manually *wifi_pruebas/start.sh* bash script.

## Simulated beacons deployed

| Time (seconds) | Beacon data |
|--|--|
| 10 to 20 | Baby seat: Insecure |
| 20 to 30 | Baby seat: Secure |
| 50 to 60 | Traffic light: Green |
| 80 to 90 | Road state: dry | 
| 110 to 120 | Bicicle: moving |

> The time here shown is approximate and relative to the start of simulation

## Usage

Only execute in Raspberry Pi terminal:

    python /home/pi/MOTAM/simulation/startSimulation.py
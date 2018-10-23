#!/usr/bin python

####################################################
# Python Script for scanning Traffic Light updates #
# MOTAM Project                                    #
# Created by Manuel Montenegro, 15-10-2018         #
####################################################

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import serial, time

class TrafficLightScanner:
    def __init__(self):
        self.serialData = serial.Serial('/dev/ttyACM0',115200)
        self.trafficStatusDict = {}

    def readAdvertisement (self):
        adv = self.serialData.readline().rstrip()
        try:
            status = adv[34:36]
            timeout = int(adv[36:38],16)

            if status == '00':
                self.trafficStatusDict['status']='red' 
            elif status == '01':
                self.trafficStatusDict['status']='yellow'
            elif status == '02':
                self.trafficStatusDict['status']='green'

            self.trafficStatusDict['timeout']=int(timeout)

        except:
            pass

        return self.trafficStatusDict

class LightWidget(QWidget):
    def __init__(self, colour):
        super(LightWidget, self).__init__()
        self.colour = colour
        self.onVal = False
    def isOn(self):
        return self.onVal
    def setOn(self, on):
        if self.onVal == on:
            return
        self.onVal = on
        self.update()
    def turnOff(self):
        self.setOn(False)
    def turnOn(self):
        self.setOn(True)
    def paintEvent(self, e):
        if not self.onVal:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setBrush(self.colour)
        painter.drawEllipse(0, 0, self.width(), self.height())

class TrafficLightWidget(QWidget):
    def __init__(self):
        super(TrafficLightWidget, self).__init__()
        vbox = QVBoxLayout(self)
        self.timeoutLabel = QLabel()
        self.timeoutLabel.setStyleSheet('color: white; font-size: 35pt')
        vbox.addWidget(self.timeoutLabel)
        self.timeoutLabel.setAlignment(Qt.AlignHCenter)
        self.redLight = LightWidget(Qt.red)
        vbox.addWidget(self.redLight)
        self.yellowLight = LightWidget(Qt.yellow)
        vbox.addWidget(self.yellowLight)
        self.greenLight = LightWidget(Qt.green)
        vbox.addWidget(self.greenLight)
        pal = QPalette()
        pal.setColor(QPalette.Background, Qt.black)
        self.setPalette(pal)
        self.setAutoFillBackground(True)

def updateState ():
    trafficLightReport = scanner.readAdvertisement()
    widget.timeoutLabel.setNum(trafficLightReport['timeout'])
    if trafficLightReport['status'] == 'red':
        widget.redLight.turnOn()
        widget.yellowLight.turnOff()
        widget.greenLight.turnOff()
    elif trafficLightReport['status'] == 'yellow':
        widget.yellowLight.turnOn()
        widget.redLight.turnOff()
        widget.greenLight.turnOff()
    elif trafficLightReport['status'] == 'green':
        widget.greenLight.turnOn()
        widget.redLight.turnOff()
        widget.yellowLight.turnOff()
    timer.start()

if __name__ == '__main__':
    import sys
    app = QApplication(sys.argv)
    vbox = QVBoxLayout()
    widget = TrafficLightWidget()
    vbox.addWidget(widget)
    vbox.setContentsMargins(0, 0, 0, 0)
    widget.resize(100, 375)
    widget.show()

    scanner = TrafficLightScanner()

    timer = QTimer ()
    timer.setInterval(1)
    timer.timeout.connect(updateState)
    timer.setSingleShot(True)
    timer.start()
    sys.exit(app.exec_())
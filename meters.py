#!/usr/bin/python3
from __future__ import print_function
import argparse
import binascii
import os
import sys
import time
import json
import datetime
import threading
import time
import flask
from bluepy import btle
import flask

# Flask configuration
app = flask.Flask(__name__)
app.config["DEBUG"] = True

# API Configuration
API_HOST="192.168.1.233"
API_PORT=5000

# SwitchBot Meter Configuration
METER_ROOMS = ['Bedroom']
METER_MACS = ['e8:fe:50:d1:75:dd']
debug_level = 1

# Collection of latest meter readings
CACHED_METER_READING = []

if os.getenv('C', '1') == '0':
    ANSI_RED = ''
    ANSI_GREEN = ''
    ANSI_YELLOW = ''
    ANSI_CYAN = ''
    ANSI_WHITE = ''
    ANSI_OFF = ''
else:
    ANSI_CSI = "\033["
    ANSI_RED = ANSI_CSI + '31m'
    ANSI_GREEN = ANSI_CSI + '32m'
    ANSI_YELLOW = ANSI_CSI + '33m'
    ANSI_CYAN = ANSI_CSI + '36m'
    ANSI_WHITE = ANSI_CSI + '37m'
    ANSI_OFF = ANSI_CSI + '0m'

class MeterReading:
    def __init__(self, time, temperature, humidity, battery):
        self.time = time
        self.temperature = temperature
        self.humidity = humidity
        self.battery = battery

# Responsible for scanning Bluetooth devices for SwitchBot Meter
class ScanProcessor():
    def handleDiscovery(self, dev, isNewDev, isNewData):
        try:
            if dev.addr in METER_MACS:
                i = 0
                room = METER_ROOMS[METER_MACS.index(dev.addr)]
                if debug_level == 1:
                    print ('\nRoom: %s Device: %s (%s), %d dBm %s. ' %(ANSI_WHITE + room + ANSI_OFF,ANSI_WHITE + dev.addr + ANSI_OFF,dev.addrType,dev.rssi,('' if dev.connectable else '(not connectable)')), end='')
                for (sdid, desc, value) in dev.getScanData():
                    i=i+1
                    if debug_level == 1:
                        print( str(i) + ': ' + str(sdid) + ', '+ desc + ', ' + value)
                    
                    #Model T (WOSensorTH) example Service Data: 000d54006400962c
                    if desc == '16b Service Data':
                        if value.startswith('000d'):
                            byte2 = int(value[8:10],16)
                            battery = (byte2 & 127)
                            byte3 = int(value[10:12],16)
                            byte4 = int(value[12:14],16)
                            byte5 = int(value[14:16],16)
                            tempc = float(byte4-128)+float(byte3 / 10.0)
                            humidity = byte5
                            self._publish(room, tempc, humidity, battery)
                        else:
                            if debug_level == 1:
                                print(value.len())
    
                if not dev.scanData:
                    print ('(no data)')
                    print

        except:
            print("handleDiscovery: Oops!",sys.exc_info()[0],"occurred.")

    def _publish(self, room, tempc, humidity, battery):
        try:
            now = datetime.datetime.now()
            topic = '{}/{}'.format(room.lower(), 'meter')
            timeNow = now.strftime("%Y-%m-%d %H:%M:%S")
            msgdata = '{"time":\"' + timeNow + '\","temperature":' + str(tempc) + ',"humidity":' + str(humidity) + ',"battery":' + str(battery) +'}'

            # Save the meter reading to file
            CACHED_METER_READING.append(
                MeterReading(timeNow, tempc, humidity, battery)
                )

            print(msgdata)
        except:
            print("_publish: Oops!",sys.exc_info()[0],"occurred.")

# Runs in the background, getting data from SwitchBot Meters and then storing it in local memory
class ScanBackgroundWorker(object):
    def __init__(self, interval=60):
        self.interval = interval

        thread = threading.Thread(target=self.run, args=())
        thread.daemon = True                            # Daemonize thread
        thread.start()                                  # Start the execution

    def run(self):
        while True:
            # Get the latest readings from the SwitchBot Meter
            scanner = btle.Scanner().withDelegate(ScanProcessor())
            scanner.scan()
            # Wait until the next interval to scan for the latest devices        
            time.sleep(self.interval)

# Shows all meter reading in local memory
@app.route('/meters', methods=['GET'])
def allMeters():
    jsonOutput = json.dumps(CACHED_METER_READING)
    print(CACHED_METER_READING)
    return jsonOutput

def main():
    ScanBackgroundWorker()
    app.run(host="192.168.1.233", port=5000, debug=True)

if __name__ == "__main__":
        main()
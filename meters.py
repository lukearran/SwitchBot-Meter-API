#!/usr/bin/python3
# Install BluePy and Paho MQTT Libraries
# The run command on a Raspberry Pi is
# sudo python3 meters.py 
from __future__ import print_function
import argparse
import binascii
import os
import sys
import time
import datetime
from bluepy import btle
import paho.mqtt.client as mqtt

# Modify the following for your setup....
METER_ROOMS = ['Room1','Room2','Room3']
METER_MACS = ['xx:xx:xx:xx:xx:xx','xx:xx:xx:xx:xx:xx','xx:xx:xx:xx:xx:xx']
MQTT_USERNAME = 'xxxxxxxx'
MQTT_PASSWORD = 'xxxxxxxx'
MQTT_HOST = '192.168.1.100'
MQTT_PORT = 1883
MQTT_TIMEOUT = 30
debug_level = 1
#
# I use a stack for the MQTT Messages because sometimes the BLE Scan data is read
# before the MQTT Connection. I should probbaly change the logic path, but since it
# works, I'll leave as is.
MQTT_TOPIC_STACK = {""}
MQTT_PAYLOAD_STACK = {""}

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


class ScanProcessor():

    def __init__(self):
        self.mqtt_client = None
        self.connected = False
        self._start_client()


    def handleDiscovery(self, dev, isNewDev, isNewData):
        try:
            if isNewDev and dev.addr in METER_MACS:
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
                            if debug_level == 1:
                                print('\nPublishing...'+room)
                            self._publish(room, tempc, humidity, battery)
     
                        else:
                            if debug_level == 1:
                                print(value.len())
    
                    #else:
                        #print('No 16b Service Data')
    
                if not dev.scanData:
                    print ('(no data)')
                    print

        except:
            print("handleDiscovery: Oops!",sys.exc_info()[0],"occurred.")


    def _start_client(self):
        self.mqtt_client = mqtt.Client()
        self.mqtt_client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)

        def _on_connect(client, _, flags, return_code):
            self.connected = True
            if debug_level == 1:
                print("on_connect: MQTT connection returned result: %s" % mqtt.connack_string(return_code))

        def on_disconnect(client, userdata, return_code):
            if rc != 0:
                print("Unexpected disconnection: "+ return_code)
            else:
                print("Disconnected.")

        def _on_publish(client, userdata, mid):
            if debug_level == 1:
                info = 'on_publish: {}, {}, {}'.format(client,userdata,str(mid))
                print(info)

        def _on_log(mqttc, obj, level, string):
            if debug_level == 1:
                print('on_log: ' + string)

        self.mqtt_client.on_connect = _on_connect
        self.mqtt_client.on_publish = _on_publish
        self.mqtt_client.on_log = _on_log

        self.mqtt_client.connect(MQTT_HOST, MQTT_PORT, MQTT_TIMEOUT)
        self.mqtt_client.loop_start()

    def _publish(self, room, tempc, humidity, battery):
        try:
            now = datetime.datetime.now()
            topic = '{}/{}'.format(room.lower(), 'meter')
            timeNow = now.strftime("%Y-%m-%d %H:%M:%S")
            msgdata = '{"time":\"' + timeNow + '\","temperature":' + str(tempc) + ',"humidity":' + str(humidity) + ',"battery":' + str(battery) +'}'
            MQTT_TOPIC_STACK.add(topic)
            MQTT_PAYLOAD_STACK.add(msgdata)
            if self.connected:
                while len(MQTT_TOPIC_STACK) > 0:
                    t = MQTT_TOPIC_STACK.pop()
                    p = MQTT_PAYLOAD_STACK.pop()
                    if len(t) > 0:
                        if debug_level == 1:
                            print('STACK {} {} {} {}'.format(str(len(MQTT_TOPIC_STACK)),timeNow,t,p))
                        self.mqtt_client.publish(t, p, qos=0, retain=True)
                        print('Sent data to topic %s: %s ' % (topic, msgdata))
        except:
            print("_publish: Oops!",sys.exc_info()[0],"occurred.")

def main():

    scanner = btle.Scanner().withDelegate(ScanProcessor())

    print (ANSI_RED + "Scanning for devices..." + ANSI_OFF)
    devices = scanner.scan(30)

if __name__ == "__main__":
        main()

#!/usr/bin/env python3

"""
hjconnect.py

https://github.com/hjltu/hjconnect
install: pip3 paho-mqtt psutils
usage: python3 hjconnect.py

* changelog:
12-Nov-18 start working
24-dec-18 status
02-jan-19 add shell
07-jan-19 add file transfer

* ANSI codes
 17 http://www.lihaoyi.com/post/BuildyourownCommandLinewithANSIescapecodes.html

* pep8
pip install pep8
pep8 --show-source --show-pep8 testfile.py

"""

import os
import sys
import time
import _thread
import threading
import paho.mqtt.client as mqtt
# encription
import socket
import ssl

from lib import mylib
from lib import hjstat
from lib import hjshell

import inspect
current_dir = os.path.dirname(os.path.abspath(inspect.getfile(inspect.currentframe())))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)
from config.hjhome import VERSION, CONN_LTOPIC, CONN_RTOPIC, CONN_GAP, \
    CONN_REMOTE_SERVER, MQTT_SERVER, CONN_REMOTE_PORT, CONN_LOCAL_PORT, \
    CONN_ENCRYPTION, CONN_CA_CRT
from setup.rpi_serial import serial as SERIAL

CRT = "../config/" + CONN_CA_CRT
NAME = " * "+__file__+" * "
RTOPIC = CONN_RTOPIC + SERIAL

def event(client, top, msg):
    """
    handling message from client
    """
    for msg in hjshell.my_command(top, msg):
        if client == "local":
            mylib.my_log(NAME+"local event "+str(msg))
            top = CONN_LTOPIC+"/out"
            lclient.publish(top, mylib.my_json(msg))
        if client == "remote":
            mylib.my_log(NAME+"remote event"+str(msg))
            top = RTOPIC + "/out"
            rclient.publish(top, mylib.my_json(msg))


def my_stat():
    """
    RPI status, GAP is period
    """
    time.sleep(3)
    payload = hjstat.my_stat()
    rclient.publish(RTOPIC + "/out/status", mylib.my_json(payload))
    th = threading.Timer(CONN_GAP, my_stat)
    th.daemon = True
    th.start()


# local client
def l_connect(client, userdata, flags, rc):
    mylib.my_log(
        NAME+"Connected local client with result code = "+str(rc), 1)
    payload = hjstat.my_connect(client="local", conn=True, log=1)
    lclient.publish(CONN_LTOPIC+"/out/start", mylib.my_json(payload))
    lclient.subscribe(CONN_LTOPIC+"/in/#")


def l_message(client, userdata, msg):
    _thread.start_new_thread(event, ("local", msg.topic, msg.payload,))


def run_lclient():
    payload = hjstat.my_connect(client="local", conn=False, log=0)
    lclient.will_set(CONN_LTOPIC+"/out/start", mylib.my_json(payload))
    lclient.connect(MQTT_SERVER, CONN_LOCAL_PORT, 60)
    lclient.on_connect = l_connect
    lclient.on_message = l_message
    lclient.loop_forever()


# remote client
def r_connect(client, userdata, flags, rc):
    mylib.my_log(
        NAME + "Connected remote client with result code = " + str(rc), 1)
    payload = hjstat.my_connect(client="remote", conn=True, log=1)
    rclient.publish(
        RTOPIC + "/out/start",
        mylib.my_json(payload),
        qos=1, retain=True)
    rclient.subscribe(RTOPIC + "/in/#")


def r_message(client, userdata, msg):
    _thread.start_new_thread(event, ("remote", msg.topic, msg.payload,))


def run_rclient(arg=None):
    payload = hjstat.my_connect(client="remote", conn=False, log=0)
    rclient.will_set(
        RTOPIC + "/out/start",
        mylib.my_json(payload),
        qos=1, retain=True)
    if CONN_ENCRYPTION:
        rclient.tls_set(CRT, tls_version=ssl.PROTOCOL_TLSv1_2)
        rclient.tls_insecure_set(True)
    rclient.connect(CONN_REMOTE_SERVER, CONN_REMOTE_PORT)
    rclient.on_connect = r_connect
    rclient.on_message = r_message
    rclient.loop_forever()


def main(arg=None):
    if arg == "-h":
        print(__doc__)
        return 0
    threading.Thread(target=run_lclient).start()
    threading.Thread(target=run_rclient).start()
    _thread.start_new_thread(my_stat, ())

if __name__ == "__main__":
    mylib.my_log(
        NAME+"Start "+VERSION+" subtopics: "+CONN_LTOPIC+"/in/# " +
        RTOPIC+"/in/# (shell,action)")
    rclient = mqtt.Client()     # remote
    lclient = mqtt.Client()     # local
    main()

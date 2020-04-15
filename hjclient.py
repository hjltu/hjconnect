#!/usr/bin/env python3

"""
hjclient remote shell for rpi

https://github.com/hjltu/hjconnect
usage:
    local - python3 hjclient.py
    NoRPi - python3 hjclient.py SN
    MyRPi - python3 hjclient.py 000000002254753d
    MyRPi - python3 hjclient.py 00000000c6c99a95
DIR: current directory, PID: pid may be +1, COMM: command
examples:
    ps -aux | grep command
    ping -c 4 google.com
    top -b -n 1
    sed -i -e 's/xxx/yyy/g' file
    upload filename - upload to rpi
    download filename - download from rpi
    q, exit, quit - exit
    h, hist - command history
"""

import os
import sys
import time
import _thread
import threading
import paho.mqtt.client as mqtt

import socket
import ssl

from lib import mylib
from lib import clientlib

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
history=["empty_slot"]*9


def my_exit(err):   # exit programm$
    # print("\u001b[1Aexit")
    print("exit")
    os._exit(err)
    os.kill(os.getpid)


def event(top, msg):
    """
    handling message from client
    """
    msg = mylib.byte2dict(msg)
    mylib.my_log(NAME+"event "+str(msg)+"\n")
    if type(msg) is dict:
        try:
            (msg["time"] and msg["in"] and msg["err"] and
                msg["out"] and msg["dir"] and msg["pid"])
            if msg["err"] == "lp":
                # print("\u001b[1A\u001b[32;1m>\u001b[0m", msg["out"])
                print("\u001b[32;1m>\u001b[0m", msg["out"], msg["file"])
            else:
                print(
                    "\u001b[34;1m>\u001b[0m",  # bright blue
                    msg["out"],
                    "\u001b[31;1m",
                    msg["err"],
                    "\u001b[0m",
                    "DIR:", msg["dir"],
                    ", PID:", msg["pid"],
                    ", COMM:", msg["in"])
                if msg["out"] == "download" or msg["out"] == "upload":
                    if msg["end"] is True:
                        print("file", msg["file"], "copied")
                    if msg["err"] == "":
                        msg = clientlib.out_command(msg)
                        if type(msg) is dict:
                            global ID
                            if ID is None:
                                top = CONN_LTOPIC + "/in"
                            else:
                                top = RTOPIC + str(ID) + "/in"
                            # print(top, msg)
                            client.publish(top, mylib.my_json(msg))
                    else:
                        print(
                            "\u001b[34;1m>\u001b[0m",  # bright blue
                            msg["out"],
                            "\u001b[31;1m",
                            msg["err"],
                            "\u001b[0m")
        except:
            mylib.my_log(NAME+"\u001b[33;1mMSG: \u001b[0m"+str(msg))
    print("\u001b[32;1m\u001b[1A")  # bright green


def my_input():
    global ID
    if ID is None:
        top = CONN_LTOPIC + "/in"
    else:
        top = RTOPIC + str(ID) + "/in"
    while True:
        # print("\u001b[32;1m ")    # bright green
        comm = input()
        print("\u001b[0m")  # reset color
        # mylib.my_log(NAME+str(comm))
        if comm == "exit" or comm == "quit" or comm == "q":
            my_exit(0)
        if comm == "h" or comm == "hist":
            for l in range(len(history)):
                print(l, history[l])
            continue
        try:
            comm=int(comm)
            if comm<len(history):
                comm=history[comm]
            else:
                continue
        except:
            history.pop()
            history.insert(0,comm)
        if (comm.split(" ")[0] == "upload" or
                comm.split(" ")[0] == "download"):
            msg = clientlib.in_command(comm)
            if msg["err"] == "":
                client.publish(top, mylib.my_json(msg))
            else:
                print("\u001b[31;1m", msg["err"], "\u001b[0m")
        else:
            msg = {
                "in": str(comm),
                "err": "", "file": "", "dir": "NA", "pid": "NA",
                "time": int(time.time())}
            client.publish(top, mylib.my_json(msg))
        mylib.my_log(NAME+"input "+str(msg)+"\n")


# client
def say_hi(top):
    msg = {
        "in": "MY=`pwd` && echo Welcome to Pi, You are here: $MY",
        "err": "", "time": time.time()}
    client.publish(top, mylib.my_json(msg))


def l_connect(client, userdata, flags, rc):
    mylib.my_log(
        NAME + "Connected to "+CONN_LTOPIC+" with result code = " + str(rc), 1)
    client.subscribe(CONN_LTOPIC + "/out/#")
    say_hi(LTOPIC+"/in")


def r_connect(client, userdata, flags, rc):
    global ID
    mylib.my_log(
        NAME + "Connected to " + RTOPIC + str(ID) +
        " with result code = " + str(rc), 1)
    client.subscribe(RTOPIC + str(ID) + "/out/#")
    say_hi(RTOPIC+str(ID)+"/in")


def message(client, userdata, msg):
    _thread.start_new_thread(event, (msg.topic, msg.payload,))


def run_client(arg=None):
    if arg is None:
        client.connect(MQTT_SERVER, CONN_LOCAL_PORT, 60)
        client.on_connect = l_connect
    else:
        if CONN_ENCRYPTION:
            client.tls_set(CRT, tls_version=ssl.PROTOCOL_TLSv1_2)
            client.tls_insecure_set(True)
        client.connect(CONN_REMOTE_SERVER, CONN_REMOTE_PORT, 60)
        client.on_connect = r_connect
    client.on_message = message
    client.loop_forever()


def main(arg=None):
    threading.Thread(target=run_client, args=(arg, )).start()
    _thread.start_new_thread(my_input, ())

if __name__ == "__main__":
    print(__doc__)
    mylib.my_log("Release date: "+VERSION)
    client = mqtt.Client()
    global ID
    if len(sys.argv) == 2:
        ID = sys.argv[1]
        main(ID)
    else:
        ID = None
        print("ID =", ID, "start local client")
        main()

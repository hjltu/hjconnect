#!/usr/bin/env python3

"""
hjstat

    /start json:
    "conn":     bool
    "uptime":   int
    "time":     int
    "id":       str
    "gap":      int
    "release":  str
    "timestr":  str

    /status json:
    "gap":          int
    "id":           str
    "memtotal":     int
    "memused":      int
    "disktotal":    int
    "diskfree":     int
    "cputemp":
    "cpuload":
    "internalip":   str
    "publicip":     str
    "uptime":       str
    "time":         int UTC
    "timestr":      str UTC

"""

import time
import config
from . import mylib


DEVICE_ID = mylib.get_serial()
PUBLIC_IP = mylib.get_public_ip()
# set time to UTC
# SET_DATE = mylib.set_time()
# interval
GAP = config.GAP
RELEASE = config.RELEASE
NAME = " * "+__file__+" * "


def my_ipcheck():
    return PUBLIC_IP


def my_stat():
    # check public IP address
    if "ERR" in my_ipcheck():
        global PUBLIC_IP
        mylib.my_log(NAME+'try to get public ip', 1)
        PUBLIC_IP = mylib.get_public_ip()
    # rpi status message
    payload = {
        "id": DEVICE_ID,
        "gap": GAP,
        "release": RELEASE,
        "memtotal": mylib.get_total_mem(),
        "memused": mylib.get_used_mem(),
        "disktotal": mylib.get_sd_size(),
        "diskfree": mylib.get_free_space(),
        "cputemp": mylib.get_cpu_temp(),
        "cpuload": mylib.get_cpu_usage(),
        "internalip": mylib.get_ip_addr(),
        "publicip": PUBLIC_IP,
        "uptime": mylib.get_uptime(),
        "time": int(time.time()),
        "timestr": time.ctime()}
    mylib.my_log(NAME+'status: '+str(payload))
    return payload


def my_connect(client="Local", conn=False, log=0):
    payload = {
        "conn": conn,
        "id": DEVICE_ID,
        "gap": GAP,
        "err": "", "in": "", "dir": "NA", "pid": "NA",
        "out": "Connection: "+str(conn),
        "release": RELEASE,
        "uptime": mylib.get_uptime(),
        "time": int(time.time()),
        "timestr": time.ctime()}
    mylib.my_log(NAME+client+" client: " + str(payload), log)
    return payload

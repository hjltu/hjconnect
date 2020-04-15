#!/usr/bin/env python3

"""
    libs for hjconnect.py
"""

import os
import sys
import subprocess
import json
import urllib.request
import psutil
import time
import datetime
import base64
import hashlib

sys.path.append("/root")
from config.hjhome import CONN_VERBOSE

NAME = " * "+__file__+" * "


def my_json(payload):
    return json.dumps(payload)  # object2string


def byte2dict(msg):
    if type(msg) is bytes:
        try:
            msg = msg.decode()
            msg = json.loads(msg)
        except Exception as e:
            msg = "ERR msg2json: "+str(e)
            my_log(NAME+msg)
    return msg


def my_exit(err):
    os._exit(err)
    os.kill(os.getpid)


def get_serial():
    # Extract rpi serial from cpuinfo file
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if 'Serial' in line:
                    return str(line[10:26])
            return "SN"
    except Exception as e:
        return "ERR:" + str(e)


def get_uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            return str(datetime.timedelta(seconds=uptime_seconds))
    except Exception as e:
        return "ERR:" + str(e)


def get_total_mem():
    try:
        ram = psutil.virtual_memory()
        return ram.total
    except Exception as e:
        return "ERR:" + str(e)


def get_used_mem():
    try:
        ram = psutil.virtual_memory()
        return ram.used
    except Exception as e:
        return "ERR:" + str(e)


def get_free_space():
    try:
        disk = psutil.disk_usage('/')
        return disk.free
    except Exception as e:
        return "ERR:" + str(e)


def get_sd_size():
    try:
        disk = psutil.disk_usage('/')
        return disk.total
    except Exception as e:
        return "ERR:" + str(e)


def get_cpu_temp():
    try:
        time.sleep(1)
        res = os.popen(
            "vcgencmd measure_temp 2>&1").readline().replace("\'C\n", "")
        time.sleep(1)
        return res.split('=')[1]
    except:
        res = os.popen(
            "cat /sys/class/thermal/thermal_zone0/temp").readline().replace("\n", "")
        return int(res)/1000


def get_cpu_usage():
    try:
        return psutil.cpu_percent()
    except Exception as e:
        return "ERR:" + str(e)


def get_ip_addr():
    """ all ip addresses"""
    try:
        res = subprocess.check_output(['hostname', '-i'])
        return res.decode('utf-8').replace(" \n", "")
    except Exception as e:
        return "ERR:" + str(e)


def get_public_ip():
    try:
        res = urllib.request.urlopen('https://httpbin.org/ip')
        j = json.loads(res.read().decode('utf-8'))
        return j['origin']
    except Exception as e:
        return "ERR:" + str(e)


def set_time():
    # set UTC
    try:
        res = urllib.request.urlopen('https://now.httpbin.org')
        j = json.loads(res.read().decode('utf-8'))
        my_date = str(j['now']['rfc2822'])
        print(my_date[5:-4])
        os.system('sudo date -s "%s"' % str(my_date[5:-4]).upper())
        return my_date
    except Exception as e:
        return "ERR:" + str(e)


def my_log(msg, add=0):
    if CONN_VERBOSE:
        print(msg)
    if add == 1:
        logdir = "log"
        # check log's directory
        try:
            if not os.path.exists(logdir):
                os.makedirs(logdir)
        except Exception as e:
            print("ERR: "+str(e))
            return
        # add message to today's log file
        mydate = datetime.date.today().strftime("%d-%b-%Y")
        mytime = time.strftime("%d-%b-%y_%H:%M:%S")
        try:
            with open(logdir + "/" + mydate + ".txt", "a") as f:
                f.write(mytime + "\t" + msg + "\n")
        except Exception as e:
            print(e)
            return


def bin2str_file(file):
    with file:
        return base64.b64encode(file.read())


def my_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()

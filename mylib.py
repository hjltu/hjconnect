#!/usr/bin/env python3

"""
    libs for hjconnect.py
"""

import os, subprocess, json
import urllib.request
import psutil 
import time, datetime
#from datetime import timedelta
import logging
import base64
import hashlib

# log2mqtt
import socket, ssl
import mqtthandler

def my_json(payload):
    return json.dumps(payload)  # object2string

def my_exit(err):
    os._exit(err)
    os.kill(os.getpid)

def get_serial():
    # Extract serial from cpuinfo file for RaspberryPI
    try:
        with open('/proc/cpuinfo', 'r') as f:
            for line in f:
                if 'Serial' in line:
                    return str(line[10:26])
            return "NA"
    except Exception as e:
        return "ERR:" + str(e)

def get_uptime():
    try:
        with open('/proc/uptime', 'r') as f:
            uptime_seconds = float(f.readline().split()[0])
            uptime = str(datetime.timedelta(seconds = uptime_seconds))
            return uptime
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
        ram_used = ram.used# / 2**20
        #ram_percent_used = ram.percent
        return ram_used
    except Exception as e:
        return "ERR:" + str(e)

def get_free_space():
    try:
        disk = psutil.disk_usage('/')
        disk_free = disk.free #/ 2**30
        return disk_free
    except Exception as e:
        return "ERR:" + str(e)

def get_sd_size():
    try:
        disk = psutil.disk_usage('/')
        disk_total = disk.total
        return disk_total
    except Exception as e:
        return "ERR:" + str(e)  

def get_cpu_temp():
    try:
        res=os.popen("vcgencmd measure_temp").readline().replace("\'C\n","")
        l=res.split('=')
        return l[1]
    except Exception as e:
        return "ERR:" + str(e)

def get_cpu_usage():
    try:
        return psutil.cpu_percent()
    except Exception as e:
        return "ERR:" + str(e)

def get_ip_addr():
    try:
        res=subprocess.check_output(['hostname','-I'])
        return res.decode('utf-8').replace(" \n","")
    except Exception as e:
        return "ERR:" + str(e)

def get_public_ip():
    try:
        res=urllib.request.urlopen('https://httpbin.org/ip')
        j=json.loads(res.read().decode('utf-8'))
        return j['origin']
    except Exception as e:
        return "ERR:" + str(e)

def set_time():
    try:
        res=urllib.request.urlopen('https://now.httpbin.org')
        j=json.loads(res.read().decode('utf-8'))
        my_date=str(j['now']['rfc2822'])
        #print(my_date[5:-4])
        # set UTC time
        #os.system('sudo date -s "%s"' % str(my_date[5:-4]).upper())
        return my_date
    except Exception as e:
        return "ERR:" + str(e)

def my_log(file,msg,show=0):
    my_date = datetime.date.today().strftime(".%d-%b-%Y")

    # absolute path to this file
    full_path = os.path.realpath(__file__)
    path=os.path.split(full_path)
    # path: file[0], filename: file[1]
    file=os.path.split(file)

    logger = logging.getLogger(__name__)
    #logger.setLevel(logging.INFO)
    # create a file handler
    handler = logging.FileHandler(path[0] + "/" + file[1] + my_date + '.log')
    handler.setLevel(logging.INFO)
    # create a logging format
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)
    # add the handlers to the logger
    if (logger.hasHandlers()):
        logger.handlers.clear()
    logger.addHandler(handler)
    logger.info(file[1] + " " + str(msg))
    if show == 1:
        print(msg)

# check 'reboot' command with retain=True
def my_retain_check(command,retain):
    if retain == True:
        status.my_log(__file__,'ERR: ' + command + ' + retain')
        return True
    else:
        return False

def bin2str_file(file):
    with file:
        return base64.b64encode(file.read())

def my_md5(fname):
    hash_md5 = hashlib.md5()
    with open(fname, "rb") as f:
        for chunk in iter(lambda: f.read(4096), b""):
            hash_md5.update(chunk)
    return hash_md5.hexdigest()


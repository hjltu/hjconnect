#!/usr/bin/env python3

"""
    /start json:
    "conn":     bool
    "uptime":   int
    "time":     int
    "id":       str
    "timestr":  str

    /status json:
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

    usage: python3 hjconnect.py [-l]

    changelog:
    12-Nov-18 start working
"""

import os,sys,time
import _thread,threading
import paho.mqtt.client as mqtt
#import socket, ssl
import mylib


VERSION = "22-Dec-18"

DEVICE_ID = mylib.get_serial()
PUBLIC_IP = mylib.get_public_ip()
#SET_DATE = mylib.set_time()
TOPIC = "/hjconnect/"+DEVICE_ID

def my_check_date():
    if 'ERR' in SET_DATE:
        return False
    else:
        return True

def my_check_ip():
    if 'ERR' in PUBLIC_IP:
        return False
    else:
        return True

def l_event(top,msg):
    print("local event",top,msg)

def r_event(top,msg):
    print("remote event",top,msg)

def my_stat():
    time.sleep(3)
#    if my_check_date() is False:
#        global SET_DATE
#        mylib.my_log('try to set_date')
#        SET_DATE = mylib.set_time()
    if my_check_ip() is False:
        global PUBLIC_IP
        mylib.my_log('try to get public ip',1)
        PUBLIC_IP = mylib.get_public_ip()
    payload={"id": DEVICE_ID, \
    "memtotal": mylib.get_total_mem(), \
    "memused": mylib.get_used_mem(), \
    "disktotal": mylib.get_sd_size(), \
    "diskfree": mylib.get_free_space(), \
    "cputemp": mylib.get_cpu_temp(), \
    "cpuload": mylib.get_cpu_usage(), \
    "internalip": mylib.get_ip_addr(), \
    "publicip": PUBLIC_IP, \
    "uptime": mylib.get_uptime(), \
    "time": int(time.time()), \
    "timestr": time.ctime()}
    mylib.my_log('status: '+str(payload),1)
    rclient.publish(TOPIC+"/out/status", mylib.my_json(payload))
    th=threading.Timer(9,my_stat) # interval
    th.daemon=True
    th.start()

### local client ###

def l_connect(client, userdata, flags, rc):
    mylib.my_log("Connected local client with result code = "+str(rc),1)
    payload={"conn": True, \
    "uptime":mylib.get_uptime(), \
    "time": int(time.time()), \
    "timestr": time.ctime()}
    mylib.my_log("Local client: " + str(payload),1)
    lclient.publish("/hjlocal/out/start", mylib.my_json(payload))

def l_message(client, userdata, msg):
   _thread.start_new_thread(l_event,(msg.topic,msg.payload,))

def run_lclient():
    payload={"conn": False, \
    "uptime":mylib.get_uptime(), \
    "time": int(time.time()), \
    "timestr": time.ctime()}
    lclient.will_set("/hjlocal/out/start", mylib.my_json(payload))
    lclient.connect("localhost",1883,60)
    lclient.on_connect = l_connect
    lclient.on_message = l_message
    lclient.loop_forever()

### remote client ###

def r_connect(client, userdata, flags, rc):
    mylib.my_log("Connected remote client with result code = "+str(rc),1)
    payload={"conn": True, \
    "uptime":mylib.get_uptime(), \
    "time": int(time.time()), \
    "id": DEVICE_ID, \
    "timestr": time.ctime()}
    mylib.my_log("Remote client: " + str(payload),1)
    rclient.publish(TOPIC+"/out/start", mylib.my_json(payload), qos=1, retain=True)

def r_message(client, userdata, msg):
   _thread.start_new_thread(r_event,(msg.topic,msg.payload,))

def run_rclient(arg=None):
    payload={"conn": False, \
    "uptime":mylib.get_uptime(), \
    "time": int(time.time()), \
    "id": DEVICE_ID, \
    "timestr": time.ctime()}
    rclient.will_set(TOPIC+"/out/start", mylib.my_json(payload), qos=1, retain=True)
    if arg == '-l':
        rclient.connect("localhost",1883,60)
    else:
        #rclient.username_pw_set("admin", "public")
        #rclient.tls_set("/etc/ssl/certs/mycert.pem", None, None, cert_reqs=ssl.CERT_NONE, tls_version=ssl.PROTOCOL_TLSv1_2 )
        #rclient.tls_insecure_set(True)
        #rclient.connect("myip",443)
        rclient.connect("test.mosquitto.org",1883,60)
    rclient.on_connect = r_connect
    rclient.on_message = r_message
    rclient.loop_forever()

def main(arg=None):
    if arg == "-h":
        print(__doc__)
        return 0
    threading.Thread(target=run_lclient).start()
    threading.Thread(target=run_rclient,args=(arg,)).start()
    #_thread.start_new_thread(start_lclient,())
    #_thread.start_new_thread(start_rclient,(arg,))
    _thread.start_new_thread(my_stat,())

if __name__ == "__main__":
    rclient = mqtt.Client() # remote
    lclient = mqtt.Client() # local
    if len(sys.argv) == 2:
        main(sys.argv[1])
    else:
        main()


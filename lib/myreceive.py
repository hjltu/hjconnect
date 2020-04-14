#!/usr/bin/env python3

"""
myreceive.py - save file on server(upload)

    "in":           "upload"
    "id":           device ID
    "out":          "upload"
    "time":         timestamp, message ID
    "file":         file name
    "dir":          path to file
    "size":         file size
    "hash":         file hash (md5)
    "data":         chunk of the file
    "chunkhash":    hash of the chunkdata (md5)
    "chunknumber":  number of chunkdata, numbered from (0 - null,zero)
    "encode":       chunkdata encoding type (base64)
    "end":          end of message (True - end)

test example:
echo "test" > test.txt
mosquitto_pub -t /hjlocal/in -m \
'{"in":"upload","time":1234,"file":"test.txt","dir":".","chunknumber":1,"data":"dGVzdAo=","chunkhash":"99ec4b704e3d5abdcd7c66a351b24b1c","end":false}'
mosquitto_pub -t /hjlocal/in -m \
'{"in":"upload","time":1234567,"file":"test.txt","dir":"tmp","data":"","hash":"d8e8fca2dc0f896fd7cb4cb0031ba249","end":true}'
"""

import os
import base64
import hashlib
import config
from . import mylib


NAME = " * "+__file__+" * "
TMPDIR = config.TMPDIR


def my_file_end(msg):
    os.sync()
    for l in os.listdir(TMPDIR):
        try:
            int(l.split("_")[0])
        except:
            continue
        timeid = int(l.split("_")[0])
        if timeid == msg["time"]:
            if mylib.my_md5(TMPDIR+"/"+l) == msg["hash"]:
                try:
                    os.rename(TMPDIR+"/"+l, TMPDIR+"/"+msg["file"])
                    mylib.my_log(NAME+"file: \""+msg["file"]+"\" saved")
                except Exception as e:
                    error = "ERR: "+str(e)
                    mylib.my_log(NAME+error)
                    msg["err"] = error
            else:
                error = "ERR: hash does not match"
                mylib.my_log(NAME+error)
                msg["err"] = error
    return msg


def my_file_write(msg):
    """check data == hash and save data to temp file"""

    if hashlib.md5(msg["data"].encode()).hexdigest() == msg["chunkhash"]:
        fname = TMPDIR+"/"+str(msg["time"])+"_"+str(msg["file"])+"_.temp"
        try:
            if msg["chunknumber"] == 0:
                f = open(fname, "wb")
            else:
                f = open(fname, "ab")
            f.write(base64.b64decode(msg["data"]))
        except Exception as e:
            error = "ERR: "+str(e)
            mylib.my_log(NAME+error)
            msg["err"] = error
        finally:
            f.close()
            msg["data"] = ""
            mylib.my_log(NAME+" write "+fname)
    return msg


def my_receive(msg):
    msg["out"] = msg["in"]
    # check json
    try:
        msg["end"] and msg["hash"]
    except:
        error = "ERR wrong json: no \"end\" or \"hash\""
        mylib.my_log(NAME+error)
        msg["err"] = error
        return msg
    # prepare directory
    try:
        if not os.path.isdir(TMPDIR):
            os.makedirs(TMPDIR)
    except Exception as e:
        error = "ERR: "+str(e)
        mylib.my_log(NAME+error)
        msg["err"] = error
        return msg

    if msg["end"] is True:
        return my_file_end(msg)
    if msg["end"] is False:
        try:
            msg["chunkhash"] and msg["chunknumber"]
        except:
            error = "ERR wrong json: no \"chunkhash\" or \"chunlnumber\""
            mylib.my_log(NAME+error)
            msg["err"] = error
            return msg
        return my_file_write(msg)

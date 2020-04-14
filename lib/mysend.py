#!/usr/bin/env python3

"""
mysend.py

    "in":           download
    "id":           device ID
    "time":         timestamp from input message
    "dir":          path
    "file":         file name
    "size":         file size
    "hash":         file hash (md5)
    "data":         chunk of the file
    "chunkhash":    hash of the chunkdata (md5)
    "chunksize":    size of the chunkdata
    "chunknumber":  number of chunkdata, numbered from (0 - null,zero)
    "encode":       chunkdata encoding type (base64)
    "end":          end of file (True - end)

"""

import os
import time
import base64
import hashlib
from . import mylib


NAME = " * "+__file__+" * "


def my_file_read(msg):
    filepath = str(msg["dir"])+"/"+str(msg["file"])
    if not os.path.isfile(filepath):
        error = "ERR: file \""+filepath+"\" not find"
        mylib.my_log(NAME+error)
        msg["err"] = error
        return msg
    shift = int(msg["chunknumber"])*int(msg["chunksize"])
    try:
        f = open(filepath, "rb")
        if shift > 0:         # check file begin
            f.seek(shift)
        chunk = f.read(int(msg["chunksize"]))
        msg["data"] = base64.b64encode(chunk).decode()
        msg["hash"] = mylib.my_md5(filepath)
        if len(msg["data"]) > 0:
            msg["chunkhash"] = hashlib.md5(msg["data"].encode()).hexdigest()
            msg["end"] = False
        else:
            msg["end"] = True
    except Exception as e:
        error = "ERR file read: " + str(e)
        mylib.my_log(NAME+error)
        msg["err"] = error
    finally:
        f.close()
        mylib.my_log(NAME+" read "+filepath)
    return msg


def my_send(msg):
    msg["out"] = msg["in"]
    try:
        msg["chunknumber"] and msg["chunksize"]
    except:
        error = "ERR: no \"chunkhash\" in json"
        mylib.my_log(NAME+error)
        msg["err"] = error
        return msg
    outmsg = my_file_read(msg)
    return outmsg

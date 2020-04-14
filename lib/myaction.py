#!/usr/bin/env python3

"""
myaction.py

"in":           download or upload
"id":           device ID
"time":         timestamp, from input message(msg["time"])
"file":         file name
"size":         file size
"hash":         file hash (md5)
"data":         chunk of the file
"chunkhash":    hash of the chunkdata (md5)
"chunknumber":  number of chunkdata, numbered from (0 - null,zero)
"encode":       chunkdata encoding type (base64)
"end":          end of message (True - end)

"""

from . import mylib
from . import mysend
from . import myreceive


NAME = " * "+__file__+" * "


def action(msg):
    try:
        msg["file"] and msg["dir"]
    except:
        msg["err"] = "ERR: no \"file\" or \"dir\" in message"
        mylib.my_log(NAME+msg["err"])
        return msg
    if msg["in"] == "upload":
        mylib.my_log(NAME+"upload")
        return myreceive.my_receive(msg)
    if msg["in"] == "download":
        mylib.my_log(NAME+"download")
        return mysend.my_send(msg)

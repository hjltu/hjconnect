#!/usr/bin/env python3

"""
clientlib.py
"""

import time
import config
from . import mysend
from . import myreceive
from . import mylib


CHUNKSIZE = config.CHUNKSIZE
NAME = " * "+__file__+" * "


def out_command(msg):
    if msg["out"] == "upload":
        return out_upload(msg)
    if msg["out"] == "download":
        return out_download(msg)


def out_upload(msg):
    # print(msg)
    # print(type(msg["chunknumber"]))
    if msg["end"] is False and msg["err"] == "":
        msg["chunknumber"] += 1
        msg["pid"] = msg["chunknumber"]
        return mysend.my_send(msg)


def out_download(msg):
    msg = myreceive.my_receive(msg)
    if msg["end"] is False and msg["err"] == "":
        msg["chunknumber"] += 1
        msg["pid"] = msg["chunknumber"]
        return msg


def in_command(comm):
    if len(comm.split(" ")) == 2:
        comm = comm.split()
        if len(comm[1].split("/")) > 1:
            myfile = comm[1].rsplit("/", 1)
            mypath = myfile[0]
            myfile = myfile[1]
        else:
            mypath = "."
            myfile = comm[1]
        payload = {
            "in": comm[0],
            "err": "",
            "pid": "NA",
            "time": int(time.time()),
            "file": myfile,
            "dir": mypath,
            "chunknumber": 0,
            "chunksize": CHUNKSIZE}
        if comm[0] == "upload":
            return mysend.my_send(payload)
        if comm[0] == "download":
            return payload
    else:
        error = "ERR: wrong command "+comm
        mylib.my_log(NAME+error)
        return {"err": error}

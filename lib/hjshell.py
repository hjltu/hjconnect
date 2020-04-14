#!/usr/bin/env python3

"""
    hjshell
check input and send it to shell or action

myshell - bash commands.
    command for shell mode:
myaction - my special commands
    command for action mode:
    upload - upload file to rpi,
    download - download file from rpi.

json:
    in:         str, command
    out:        str, command output
    time:       int, id from input
    err:        str, error
    exitcode:   int, exitcode
    *dir:       str, current path or path to file
    *file:      str, filename

* for action mode
"""

import os
import time
from . import mylib
from . import myshell
from . import myaction

NAME = " * " + __file__ + " * "


def my_command(top, msg):
    msg = mylib.byte2dict(msg)
    if type(msg) is dict:
        try:
            msg["time"] and msg["in"] and msg["err"]
        except:
            msg["err"] = "ERR: no \"time\" in json"
            mylib.my_log(NAME + msg["err"])
            yield msg
            return
        if (msg["in"] == "upload" or
                msg["in"] == "download"):
            yield myaction.action(msg)
        else:
            for out in myshell.shell(msg):
                yield out
    else:
        error = "ERR: not json, msg is " + str(type(msg))
        mylib.my_log(NAME + error)
        yield {"err": error}

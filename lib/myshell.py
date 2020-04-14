#!/usr/bin/env python3

"""
myshell - send your command to shell

examples:
    ping -c 4 google.com
    top -b -n 1
    sed -i -e 's/xxx/yyy/g' file

"""

import os
import time
import subprocess
from . import mylib


NAME = " * "+__file__+" * "


def shell(msg):
    comm = " ".join(msg["in"].split())   # remove duplicate spaces
    currdir = os.getcwd()   # get current directory

    # launch shell process
    process = subprocess.Popen(
        comm, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, cwd=currdir)
    pid = process.pid   # get pid for process, not for command!
    mylib.my_log(NAME+'pid: '+str(pid)+', process: '+comm)
    try:
        out, err = process.communicate(timeout=3)   # wait for end process
    except subprocess.TimeoutExpired:
        mylib.my_log(
            NAME + 'WARNING: timeout for process "' +
            comm + '" with pid = ' + str(pid))
        gap = time.time()   # start time
        gap_out = ''        # all output

        # loop for long command like "ping" or "top -b"
        while True:
            if time.time() < gap+1:     # period sec
                # non blocking one line output
                out = process.stdout.readline().decode()
                gap_out += out  # addition every output line
                if not out:
                    break
            else:
                gap = time.time()
                outmsg = {
                    "in": comm,
                    "out": gap_out,
                    "err": "lp",    # long pulling
                    "pid": pid,
                    "dir": currdir,
                    "time": msg["time"]}
                gap_out = ''        # all output
                mylib.my_log(NAME+str(outmsg))
                yield outmsg
            # my_publish(command,payload)
        out, err = process.communicate()

        # all ways to kill unwanted process
        # os.kill(pid, signal.SIGTERM) # terminate long process
        # os.system('kill -9 '+str(pid))
        # process.kill()
        # process.terminate()

    exitcode = process.returncode
    out = out.decode('utf-8')
    err = err.decode('utf-8')
    outmsg = {
        "in": comm,
        "out": out,
        "pid": pid,
        "dir": currdir,
        "err": err,     # red color and reset
        "exitcode": exitcode,
        "time": msg["time"]}
    mylib.my_log(NAME+str(outmsg))

    # change current dir
    if comm.split()[0] == "cd":
        if len(comm.split()) == 2:
            newdir = comm.split()[1]
        else:
            newdir = os.getenv("HOME")
        try:
            os.chdir(newdir)
            outmsg["dir"] = os.getcwd()
            mylib.my_log(NAME+"change current dir to "+os.getcwd())
        except:
            mylib.my_log(NAME+"ERR: wrong directory name "+newdir)

    yield outmsg

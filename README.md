# hjconnect
remote telemetry system for raspberry pi

python3 hjconnect.py

Start message example:
/hjconnect/000000007d789969/out/start {"id": "000000007d789969", "conn": true, "time": 1545351737, "timestr": "2018-12-21 00:22:17", "uptime": "4 days, 16:32:16.560000"}

Repeating message example:
/hjconnect/000000007d789969/out/status {"memused": 152772608, "cpuload": 0.2, "diskfree": 4953182208, "publicip": "111.222.333.444", "memtotal": 972234752, "internalip": "192.168.0.10", "id": "000000007d789969", "time": 1545411864, "uptime": "5 days, 9:14:23.290000", "disktotal": 7194439680, "cputemp": "45.1", "timestr": "2018-12-21 17:04:24"}

# hjconnect
remote telemetry system for raspberry pi

python3 hjconnect.py -l

Start message example:
/hjconnect/000000007d789969/out/start
{<br>
  "id": "000000007d789969",<br>
  "conn": true,<br>
  "time": 1545351737,<br>
  "timestr": "2018-12-21 00:22:17",<br>
  "uptime": "4 days,<br>
  16:32:16.560000"<br>
}<br>

Repeating message example:
/hjconnect/000000007d789969/out/status 
{<br>
  "memused": 152772608,<br>
  "cpuload": 0.2,<br>
  "diskfree": 4953182208,<br>
  "publicip": "111.222.333.444",<br>
  "memtotal": 972234752,<br>
  "internalip": "192.168.0.10",<br>
  "id": "000000007d789969",<br>
  "time": 1545411864,<br>
  "uptime": "5 days, 9:14:23.290000",<br>
  "disktotal": 7194439680,<br>
  "cputemp": "45.1",<br>
  "timestr": "2018-12-21 17:04:24"<br>
}<br>

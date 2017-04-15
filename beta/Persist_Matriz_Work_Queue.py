#!/usr/bin/python
import time
import zmq
import sys

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:33002")

if sys.argv[1] == "persist" :
   socket.send("persist")
else :
   socket.send("monitor")
message = socket.recv()
print message





#!/usr/bin/python
import subprocess
import time
import zmq

command = ["mpirun", "-n", "4", "./Computation.py", "8081"]

p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

context = zmq.Context()
socket = context.socket(zmq.REQ)
socket.connect("tcp://localhost:8081")

while p.poll() == None:
   socket.send("REQ")
   message = socket.recv()
   print "Process still executing..."
   print message
   time.sleep(5) 

# p.terminate()
(stdout, stderr) = p.communicate()

print stdout
print stderr




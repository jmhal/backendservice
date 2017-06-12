#!/usr/bin/python
import time
import zmq
import sys
import subprocess
from multiprocessing import Process, Value

# create zmq context
context = zmq.Context()

def start_computation(load_list, number_of_processes, output_file_prefix, progress):
   last_load = 0   
   for i in len(load_list):
      command = ["mpirun", "-machinefile", "machinefile", "-np", str(number_of_processes), 
                 "repositorios/elastichpc/beta/trials/Matrix_Work_Queue.py", 
                  str(load_list[i]), "50", "0", output_file_prefix + "_" + str(load)]
      
      p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)

      socketOut = context.socket(zmq.REQ)
      socketOut.connect("tcp://localhost:33002")
      last_line = 0

      while p.poll() == None:
         socketOut.send("monitor") 
         last_line = int(socketOut.recv())
         progress.value = last_load + last_line
         time.sleep(5)
       
      socketOut.close() 
      last_load += load_list[i]
      progress.value = last_load

if __name__ == "__main__":
   socketIn = context.socket(zmq.REP)
   socketIn.bind("tcp://*:33001")

   load_list = None
   load_process = None
   progress = Value('i', 0, lock = True)

   _file = open("machinefile", "r+")
   lines = [line.rstrip() for line in _file.readlines()]
   p = len([line for line in lines if line])

   while True:
      message = socketIn.recv()
      if message.split(':')[0] == "load":
         load_list = [ int(e) for e in message.split(':')[1:] ]
      else if message == "start":
         if load_list != None:
            load_process = Process(target = start_computation, args=(load_list, p * 2, "teste", progress))
            load_process.daemon = True
            load_process.start()
      else if message == "state":
         socketIn.send(str(progress.value))    
      else:
         socketIn.send("wrong action.")
    
   socketIn.close() 



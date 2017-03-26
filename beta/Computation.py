#!/usr/bin/python

import random
import time
import sys
import zmq
from mpi4py import MPI
from multiprocessing import Process, Value

def sensor_reading(port, sensor):
   context = zmq.Context()
   socket = context.socket(zmq.REP)
   socket.bind("tcp://*:" + str(port.value))
   while True:
      message = socket.recv()
      socket.send(time.ctime() + " Value:" + str(sensor.value))
 
if __name__ == "__main__":
   # Sensor data structure
   sensor = Value('i', 0)
   port = Value('i', int(sys.argv[1]))

   # MPI initialization
   comm = MPI.COMM_WORLD
   size = comm.Get_size()
   rank = comm.Get_rank()

   # Monitoring process creation
   p = None
   if rank == 0:
      p = Process(target=sensor_reading, args=(port,sensor))
      p.start()

   # Perform computation
   for i in range(10):
      value = random.randint(0,100)
      data = comm.gather(value, root = 0)
   
      if rank == 0:
         for i in range(size):
            sensor.value += data[i]
         print sensor.value 
      time.sleep(5)

   # Monitoring process termination
   if rank == 0:
      p.terminate()


#!/usr/bin/python
import ctypes
import sys
import logging

from multiprocessing import Process, Pipe, Value, Manager, Lock

from Platform import platform_unit as platform_unit
from Computation import computation_unit as computation_unit

# configure logging 
logging.basicConfig(filename='computational_system.log',level=logging.DEBUG, format='%(created)f|%(message)s')

def log(msg):
   logging.debug("SYSTEM: " + msg)
   return

class ReconfigurationPort():
   def __init__(self):
      # self.actuator = Value(ctypes.c_char_p, "empty", lock = True)
      manager = Manager()

      # a lock for updating/reading the machine file
      self.machine_file_lock = manager.Lock()

      # Pipes for Communication 
      self.platform_conn, self.computation_conn = Pipe()
   
   # Methods for Computation
   def add_node():
      self.computation_conn.send(["add_node"])
      return self.computation_conn.recv()

   def remove_node():
      self.computation_conn.send(["remove_node"])
      return self.computation_conn.recv()
  
   def get_sensors():
      self.computation_conn.send(["sensors"])
      return self.computation_conn.recv()
 
if __name__ == "__main__": 
   # The information of the virtual cluster
   url = sys.argv[1]
   stack_name = sys.argv[2]
   stack_id = sys.argv[3]
   computation_input = sys.argv[8]

   # A port for communication between components
   reconfiguration_port = ReconfigurationPort()

   log("Starting Platform.")
   platform = Process(target = platform_unit, args=(reconfiguration_port, url, stack_name, stack_id))
   platform.daemon = True
   platform.start()

   log("Starting Computation.")
   computation = Process(target = computation_unit, args=(reconfiguration_port, computation_input))
   computation.daemon = True
   computation.start()

   log("Waiting on Platform to finish.")
   platform.join()
   log("Waiting on Computation to finish.")
   computation.join()

   log("Good bye...")

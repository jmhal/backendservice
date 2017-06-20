#!/usr/bin/python
import ctypes
import sys
import logging

from multiprocessing import Process, Value, Manager, Lock

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

      # start, stop or reconfigure
      self.actuator = manager.Value(ctypes.c_char_p, "wait")

      # how much of the progress has been achieved
      self.sensor = Value('f', 0.0, lock = True)

      # a lock for updating/reading the machine file
      self.machine_file_lock = manager.Lock()

   def get_sensor(self):
      return self.sensor

   def get_actuator(self):
      return self.actuator

if __name__ == "__main__": 
   # The information of the virtual cluster
   url = sys.argv[1]
   stack_name = sys.argv[2]
   stack_id = sys.argv[3]
   qos_values = sys.argv[4]             # a:t:e:c:p
   qos_weights = sys.argv[5]            # wa:wt:we:wc:wp
   qos_factor = sys.argv[6]             # alfa
   qos_intervals = sys.argv[7]          # monitoring:sample:reconfiguration
   computation_input = sys.argv[8]

   # A port for communication between components
   reconfiguration_port = ReconfigurationPort()

   log("Starting Platform.")
   platform = Process(target = platform_unit, args=(reconfiguration_port, url, stack_name, stack_id, qos_values, qos_weights, qos_factor, qos_intervals))
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

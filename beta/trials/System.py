#!/usr/bin/python
import ctypes
import sys

from Platform import platform_unit as platform_unit
from Computation import computation_unit as computation_unit
from multiprocessing import Process, Value, Manager

class ReconfigurationPort():
   def __init__(self):
      # self.actuator = Value(ctypes.c_char_p, "empty", lock = True)
      manager = Manager()
      self.actuator = manager.Value(ctypes.c_char_p, "start")
      self.sensor = Value('f', 0.0, lock = True)

   def get_sensor(self):
      return self.sensor

   def get_actuator(self):
      return self.actuator

if __name__ == "__main__": 
   # The information of the virtual cluster
   credentials = sys.argv[1]
   profile = sys.argv[2]
   stack_id = sys.argv[3]
   computation_input = sys.argv[4]

   # A port for communication between components
   reconfiguration_port = ReconfigurationPort()

   platform = Process(target = platform_unit, args=(reconfiguration_port, credentials, profile, stack_id))
   platform.daemon = True
   platform.start()

   computation = Process(target = computation_unit, args=(reconfiguration_port, computation_input))
   computation.daemon = True
   computation.start()

   platform.join()
   computation.join()

   print reconfiguration_port.get_sensor().value
   print reconfiguration_port.get_actuator().value

   

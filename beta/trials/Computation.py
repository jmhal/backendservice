import logging
import time

def log(msg):
   logging.debug("COMPUTATION: " + msg)
   return

def computation_unit(reconfiguration_port, computation_input):

   # wait until platform is ready.
   while (reconfiguration_port.get_actuator().value != "start"):
      time.sleep(5)
   log("Starting Computation.")

   # just do nothing for a while
   for i in range(1,11):
      reconfiguration_port.get_sensor().value = i / 10
      log("Progress = " + str(i / 10))
      time.sleep(5)

   # finish the computation
   reconfiguration_port.get_actuator().value = "finished"
   log("Finish Computation.")

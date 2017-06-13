import time
from infrastructure.cloud import OpenStack

def platform_unit(reconfiguration_port, credentials, profile, stack_id):
   cloud = OpenStack(credentials)

   # start the computation
   reconfiguration_port.get_actuator().value = "start"

   while True:
      # monitor interval
      time.sleep(5)

      # retrieve computation state
      print reconfiguration_port.get_sensor().value

      # retrieve infrastructure state

      # run decision procedure
      
      # perform reconfiguration
      cluster.addNode(1)

      # update machine file

      # send request for computation reconfiguration
      
 


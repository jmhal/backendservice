import time
from openstack import OpenStackCloud

def platform_unit(reconfiguration_port, credentials, profile, stack_id):
   cluster = OpenStackCloud(credentials, profile, stack_id)
   cluster.get_resources().configure_machine_file()

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
      
 


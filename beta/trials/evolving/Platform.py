import time
import logging
import collections
from infrastructure.resources.client import ResourcesProxy

def log(msg):
   logging.debug("PLATFORM: " + msg)
   return

def platform_unit(reconfiguration_port, url, stack_name, stack_id):
   # create a proxy for resources control
   log(url + ":" + stack_name + ":" + stack_id)
   proxy = ResourcesProxy(url, stack_name, stack_id)

   # set up machinefile
   nodes = proxy.configure_machine_file()
   log("Number Of Nodes = " + str(nodes))

   # start time and computation
   start_time = time.time()
   reconfiguration_port.platform_conn.send(["start"])

   # wait for instructions from the computation
   command = reconfiguration_port.platform_conn.recv()
   while command[0] != "finished" :
      
      # retrieve infrastructure state:
      resource_state = proxy.get_resource_state()

      if command[0] == "add_node":
         if nodes + 1 <= 10:
            log("Adding a node.")
            reconfiguration_port.platform_conn.send(["add_node_ok"])
            proxy.add_node(1)
            with reconfiguration_port.machine_file_lock:
               nodes = proxy.configure_machine_file()
         else:
            log("Can't add a node.")
            reconfiguration_port.platform_conn.send(["contract_limit"])
      elif command[0] == "remove_node":
         if nodes - 1 >= 2 :
            log("Removing a node.")
            proxy.remove_node(1)
            with reconfiguration_port.machine_file_lock:
               nodes = proxy.configure_machine_file()
            reconfiguration_port.platform_conn.send(["remove_node_ok"])
         else:
            log("Can't remove a node.")
            reconfiguration_port.platform_conn.send(["contract_limit"])
      elif command[0] == "sensors":
         log("Returning Sensor Info.")
         reconfiguration_port.platform_conn.send([str(resource_state)])
      else :
         log("Unknown Command.")
         reconfiguration_port.platform_conn.send(["error"])

      # insert state in log
      log("State = Elapsed Time : " + str(time.time() - start_time) + "; Efficiency : " + str(resource_state) + "; Nodes : " + str(nodes))
      
      # wait for next command
      command = reconfiguration_port.platform_conn.recv()

   log("Finish Platform.")
   end_time = time.time() 
   log("Elapsed = " + str(end_time - start_time))

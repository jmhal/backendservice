import CCAPython.gov.cca
import time
import threading
import logging
import elastichpc.common.log
from multiprocessing import Process, Value, Array, Pipe

# Setting Up Log
logger = logging.getLogger('root')

def manager_unit(manager_conn, computation):
   """
   This method is the manager unit. It will dispatch requests from
   the environment to the other parallel units running the computation
   It is the same for every component. In the end, it defines an interface
   to control the computations.
   """
   while True:
      message = manager_conn.recv()
      logger.debug("Manager Unit Got Message: " + str(message))
      if message["action"] == "start":
         resources = message["resources"]
         start_status = computation.start(resources)  
         manager_conn.send({"start_status": start_status})
      elif message["action"] == "progress":
         progress = computation.getProgress()
         manager_conn.send({"progress_status" : progress})
      elif message["action"] == "update_resources":
         new_resources = message["new_resources"]
         new_resources_status = computation.setNewResources(new_resources)
         manager_conn.send({"new_resources_status" : new_resources_status})
      elif message["action"] == "persist":
         persist_status = computation.persist()
         manager_conn.send({"persist_status" : persist_status})
      elif message["action"] == "stop":
         stop_status = computation.stop()
         manager_conn.send({"stop_status" : stop_status}]
         break
   manager_conn.close()
   return  

class Computation_Unit():
   """
   This is an abstract class that must be overwritten for every component.
   I'm writing this with MPI computations in mind, where the MPI processes
   will be launch with the help of the subprocess package. Although right 
   now I'm not dealing with the environment ports, this class should also 
   be responsible for setting up a web services container. 
   """
   def __init__(self):
      raise NotImplementedError("Abstract Class.")
     
   def start(self, resources):
      raise NotImplementedError("Abstract Class.")

   def setNewResources(self, new_resources):
      raise NotImplementedError("Abstract Class.")

   def persist(self):
      raise NotImplementedError("Abstract Class.")

   def stop(self):
      raise NotImplementedError("Abstract Class.")


class ReconfigurationPort(CCAPython.gov.cca.Port):
   """
   The malleable computation component provides this port for reconfiguration from the platform.
   """
   def __init__(self, portType,  component):
      self.component = component
      super(ReconfigurationPort, self). __init__(portType)
      return

   def getComputationProgress(self):
      """
      Will return to the Platform (and the internal Reconfiguration) the progress of the Computation.
      """
      logger.debug("Retrieving Computation Progress.")
      self.component.framework_conn.send({"action" : "progress"})
      message = self.component.driver_conn.recv()
      return message["progress_status"]

   def updateResources(self, resources):
      """
      Receive a new resources description and scale the computation.
      """
      logger.debug("Updating Resources: " + str(resources))
      self.component.framework_conn.send({"action" : "update_resources", "new_resources" : resources})
      message = self.component.driver_conn.recv()
      return message["new_resource_status"]

class ExecutionControlPort(CCAPython.gov.cca.Port):
   def __init__(self, portType, component):
      self.component = component
      super(ExecutionControlPort, self).__init__(portType)
      return
      
   def persist(self):
      """
      It is up to the developer to define a persistence mechanism. 
      But this method will always return the path to a file containing the state of the computation.
      The component places this file in the file system of the root node.
      """
      raise NotImplementedError("Base Component.")

   def start(self, state = None):
      """
      Starts or restarts the computation. The state holds the path to a file inside the root node.
      It it up to the developer to define how to start the components units. 
      """
      raise NotImplementedError("Base Component.")

   def isFinished(self):
      raise NotImplementedError("Base Component.")

class MalleableComputationComponent(CCAPython.gov.cca.Component):
   """
   This the Malleable Computation Component.
   """
   def __init__(self):
      """
      Creates the reconfiguration and execution ports, and the communication pipe.
      """
      framwork_conn, computation_conn = Pipe()
      self.framework_conn = framework_conn
      self.computation_conn = compute_conn

      self.reconfigurationPort = ReconfigurationPort("elastichpc.base.computation.malleable.ReconfigurationPort", self)
      self.executionControlPort = ExecutionControlPort("elastichpc.base.computation.malleable.ExecutionControlPort", self)
      return

   def setServices(self, services):
      self.services = services
      services.addProvidesPort(self.reconfigurationPort, "ComputationReconfigurationPort", "elastichpc.base.computation.malleable.ReconfigurationPort", None)
      services.addProvidesPort(self.executionControlPort, "ExecutionControlPort", "elastichpc.base.computation.malleable.ExecutionControlPort", None)
      services.registerUsesPort("AllocationPort", "elastichpc.base.platform.malleable.AllocationPort", None)
      return 


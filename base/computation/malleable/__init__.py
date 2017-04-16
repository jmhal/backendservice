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
         state = message["state"]
         start_status = computation.start(resources, state)  
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
      elif message["action"] == "getResults":
         results_status = computation.getResults()
         manager_conn.send({"result_status" : result_status})
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
   will be launched with the help of the subprocess package. Although right 
   now I'm not dealing with the environment ports, this class should also 
   be responsible for setting up a web services container. 
   """
   def __init__(self):
      raise NotImplementedError("Abstract Class.")
     
   def start(self, resources, state):
      raise NotImplementedError("Abstract Class.")

   def setNewResources(self, new_resources):
      raise NotImplementedError("Abstract Class.")

   def persist(self):
      raise NotImplementedError("Abstract Class.")

   def stop(self):
      raise NotImplementedError("Abstract Class.")

   def getResults(self):
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
      self.component.framework_conn.send({"action" : "persist"})
      message = self.component.framework_conn.recv()
      return message["persist_status"]

   def start(self, state = None):
      """
      Starts or restarts the computation. The state holds the path to a file inside the root node.
      It it up to the developer to define how to start the components units. 
      """
      allocationPort = self.component.services.getPort("AllocationPort")
      resources = allocationPort.getResources()
      
      logger.debug("Starting Computation: Resources %s, State %s" % (str(resources), str(state)))
      computation_process = Process(target = manager_unit, args=(self.component.compute_conn, self.component.computation))
      computation_process.daemon = True
      computation_process.start();

      self.component.framework_conn.send({"action": start, "resources" : resources, "state": state})
      message = self.component.framework_conn.recv()

      return message["start_status"]

   def stop(self):
      """
      Stops the computation.
      """
      self.component.framework_conn.send({"action": "stop"})
      message = self.component.framework_conn.recv()
      return message["stop_status"]   

   def getResults(self):
      """
      Returns the result of the computation.
      """
      if self.isFinished():
         self.component.framework_conn.send({"action" : "getResults"})
         message = self.component.framework_conn.recv()
         return message["result_status"]
      else return None

   def isFinished(self):
      """
      The return of getComputationProgress must be a number.
      """
      if (self.component.reconfigurationPort.getComputationProgress() >= 1.0):
         return True
      return False

class MalleableComputationComponent(CCAPython.gov.cca.Component):
   """
   This the Malleable Computation Component.
   """
   def __init__(self):
      """
      Creates the reconfiguration and execution ports, and the communication pipe.
      """
      framework_conn, computation_conn = Pipe()
      self.framework_conn = framework_conn
      self.computation_conn = compute_conn

      # This line must be rewritten for the actual Computation Component
      self.computation = Computation_Unit()

      self.reconfigurationPort = ReconfigurationPort("elastichpc.base.computation.malleable.ReconfigurationPort", self)
      self.executionControlPort = ExecutionControlPort("elastichpc.base.computation.malleable.ExecutionControlPort", self)
      return

   def setServices(self, services):
      self.services = services
      services.addProvidesPort(self.reconfigurationPort, "ComputationReconfigurationPort", "elastichpc.base.computation.malleable.ReconfigurationPort", None)
      services.addProvidesPort(self.executionControlPort, "ExecutionControlPort", "elastichpc.base.computation.malleable.ExecutionControlPort", None)
      services.registerUsesPort("AllocationPort", "elastichpc.base.platform.malleable.AllocationPort", None)
      return 


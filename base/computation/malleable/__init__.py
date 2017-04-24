import CCAPython.gov.cca
from elastichpc import logging
from multiprocessing import Process, Value, Array, Pipe

# Setting Up Log
logger = logging.getLogger('root')

def manager_unit(component):
   """
   This method is the manager unit. It will dispatch requests from
   the environment to the other parallel units running the computation
   It is the same for every component. In the end, it defines an interface
   to control the computations.
   """
   manager_conn = component.manager_conn
   computation = component.computation_impl
   while True:
      message = manager_conn.recv()
      logger.debug("Manager Unit Got Message: " + str(message))
      if message["action"] == "start":
         resources = message["resources"]
         input_data = message["input_data"]
         start_status = computation.start(resources, input_data)  
         manager_conn.send({"start_status": start_status})
      elif message["action"] == "progress":
         progress = computation.getProgress()
         manager_conn.send({"progress_status" : progress})
      elif message["action"] == "update_resources":
         new_resources = message["new_resources"]
         new_resources_status = computation.updateResources(new_resources)
         manager_conn.send({"update_resources_status" : new_resources_status})
      elif message["action"] == "persist":
         persist_status = computation.persist()
         manager_conn.send({"persist_status" : persist_status})
      elif message["action"] == "getResults":
         results_status = computation.getResults()
         manager_conn.send({"result_status" : result_status})
      elif message["action"] == "stop":
         stop_status = computation.stop()
         manager_conn.send({"stop_status" : stop_status})
         break
   manager_conn.close()
   return  

class ComputationUnit(object):
   """
   This is an interface that defines methods for controlling the unit.
   """
   def __init__(self):
      raise NotImplementedError("Interface.")
     
   def start(self, resources, input_data):
      raise NotImplementedError("Interface.")

   def getProgress(self, new_resources):
      raise NotImplementedError("Interface.")

   def updateResources(self, new_resources):
      raise NotImplementedError("Interface.")
    
   def persist(self):
      raise NotImplementedError("Interface.")

   def getResults(self):
      raise NotImplementedError("Interface.")

   def stop(self):
      raise NotImplementedError("Interface.")

class ComputationUnitImpl(ComputationUnit):
   """
   This is an abstract class that must be overwritten for every component.
   I'm writing this with MPI computations in mind, where the MPI processes
   will be launched with the help of the subprocess package. 
   """
   pass

class ComputationUnitProxy(ComputationUnit):
   def __init__(self, component)
      self.component = component
      return
  
  def start(self, input_data = None):
      """
      Starts or restarts the computation. The state holds the path to a file inside the root node.
      It it up to the developer to define how to start the components units. 
      """
      allocation_port = self.component.services.getPort("AllocationPort")
      resources = allocation_port.getResources()
      
      logger.debug("Starting Computation: Resources %s, State %s" % (str(resources), str(input_data)))
      manager_process = Process(target = manager_unit, args=(self.component))
      manager_process.daemon = True
      manager_process.start();

      self.component.manager_process = manager_process

      self.component.framework_conn.send({"action": "start", "resources" : resources, "input_data": input_data})
      message = self.component.framework_conn.recv()

      return message["start_status"]
  
   def getProgress(self, new_resources):
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
      return message["update_resources_status"]
   
   def persist(self):
      """
      It is up to the developer to define a persistence mechanism. 
      But this method will always return the path to a file containing the state of the computation.
      The component places this file in the file system of the root node.
      """
      self.component.framework_conn.send({"action" : "persist"})
      message = self.component.framework_conn.recv()
      return message["persist_status"]

   def getResults(self):
      """
      Returns the result of the computation.
      """
      self.component.framework_conn.send({"action" : "getResults"})
      message = self.component.framework_conn.recv()
      return message["result_status"]

   def stop(self):
      """
      Stops the computation.
      """
      self.component.framework_conn.send({"action": "stop"})
      message = self.component.framework_conn.recv()
      return message["stop_status"]   


class ReconfigurationPort(CCAPython.gov.cca.Port):
   """
   The malleable computation component provides this port for reconfiguration from the platform.
   It provides a method for monitoring and updating the resources. A Computation Component might
   personalize it further, but I believe the implementations provided are enough for most cases.
   """
   def __init__(self, portType,  component):
      self.component = component
      super(ReconfigurationPort, self). __init__(portType)
      return

   def getComputationProgress(self):
      return component.computation_proxy.getProgress() 

   def updateResources(self, resources):
      return component.computation_proxy.updateResources(resources)

class MalleableComputationComponent(CCAPython.gov.cca.Component):
   """
   This the Malleable Computation Component.
   """
   def __init__(self):
      """
      Creates the reconfiguration and execution ports, and the communication pipe.
      A computation component deriving this class must perform two extra tasks:
      - Assign self.computation_impl to a rightful implementation of ComputationUnitImpl.
      - Create any other ports.
      """
      framework_conn, manager_conn = Pipe()
      self.framework_conn = framework_conn
      self.manager_conn = manager_conn
      self.computation_proxy = ComputationUnitProxy(self)
      self.computation_impl = None 

      self.reconfiguration_port = ReconfigurationPort("elastichpc.base.computation.malleable.ReconfigurationPort", self)
      return

   def setServices(self, services):
      """
      If any other port is created by a deriving component, they should also be registered. 
      """
      self.services = services
      services.addProvidesPort(self.reconfiguration_port, "ComputationReconfigurationPort", "elastichpc.base.computation.malleable.ReconfigurationPort", None)
      services.registerUsesPort("AllocationPort", "elastichpc.base.platform.malleable.AllocationPort", None)
      return 


import CCAPython.gov.cca
import time
import threading

class ComputationProgress():
   """
   This class will hold the progress of the computation (ratio between 0 and 1) and
   the time that this measure was taken. This class does not need further especialization.
   """
   def __init__(self):
      """
      A dictionnary is used to keep the log. A lock controls the update.
      """
      self.log = {}
      self.lock = threading.Lock()

   def updateProgress(self, progress):
      """
      Both components, Platform and Computation, are running on the same node.
      There is no problem in using the local time.
      """
      with self.lock:
         self.log[time.time()] = progress
   
   def retrieveProgress(self):
      """
      A copy of the log dictionnary is retrieved, not the actual object.
      """
      with self.lock:
         return self.log.copy()

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
      return self.component.computationProgress.retrieveProgress()

   def updateResources(self, resources):
      """
      Receive a new resources description and scale the computation.
      """
      raise NotImplementedError("Base Component.")

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
      for value in self.component.computationProgress.retrieveProgress().values():
         if value == 1.0:
            return True
      return False

class MalleableComputationComponent(CCAPython.gov.cca.Component):
   def __init__(self):
      self.computationProgress = ComputationProgress()
      self.reconfigurationPort = ReconfigurationPort("elastichpc.base.computation.malleable.ReconfigurationPort", self)
      self.executionControlPort = ExecutionControlPort("elastichpc.base.computation.malleable.ExecutionControlPort", self)
      return

   def setServices(self, services):
      self.services = services
      services.addProvidesPort(self.reconfigurationPort, "ComputationReconfigurationPort", "elastichpc.base.computation.malleable.ReconfigurationPort", None)
      services.addProvidesPort(self.executionControlPort, "ExecutionControlPort", "elastichpc.base.computation.malleable.ExecutionControlPort", None)
      services.registerUsesPort("AllocationPort", "elastichpc.base.platform.malleable.AllocationPort", None)
      return 


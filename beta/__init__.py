from elastichpc.base.computation.malleable import ReconfigurationPort
from elastichpc.base.computation.malleable import ExecutionControlPort
from elastichpc.base.computation.malleable import MalleableComputationComponent
from elastichpc.base.platform.malleable import AllocationPort
from elastichpc.base.platform.malleable import QoSConfigurationPort
from elastichpc.base.platform.malleable import MalleablePlatformComponent

# Computation
class MyReconfigurationPort(ReconfigurationPort):
   def updateResources(self, resources):
      print "Recursos Atualizados."

class MyExecutionControlPort(ExecutionControlPort):
   def persist(self):
      print "Persistindo."

   def start(self, state = None):
      print "Iniciando."
      allocationPort = self.component.services.getPort("AllocationPort")
      allocationPort.getResources()
      return

   def isFinished(self):
      return False

class MyMalleableComputation(MalleableComputationComponent):
   def __init__(self):
      super(MyMalleableComputation, self).__init__()
      self.reconfigurationPort = MyReconfigurationPort("elastichpc.base.computation.malleable.ReconfigurationPort", self.progressLog, self)
      self.executionControlPort = MyExecutionControlPort("elastichpc.base.computation.malleable.ExecutionControlPort", self)

# Platform
class MyAllocationPort(AllocationPort):
   def getResources(self):
      print "Enviando Recursos."

class MyQoSConfigurationPort(QoSConfigurationPort):
   def setQoSContract(self, qos = None):
      print "Contrato Recebido."

class MyMalleablePlatform(MalleablePlatformComponent):
   def __init__(self):
      self.allocationPort = MyAllocationPort("elastichpc.base.platform.malleable.AllocationPort")
      self.qosConfigurationPort = MyQoSConfigurationPort("elastichpc.base.platform.malleable.QoSConfigurationPort")
      return


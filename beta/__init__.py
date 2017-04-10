import time
from multiprocessing import Process, Value, Array

from elastichpc.base.computation.malleable import ReconfigurationPort
from elastichpc.base.computation.malleable import ExecutionControlPort
from elastichpc.base.computation.malleable import MalleableComputationComponent
from elastichpc.base.computation.malleable import ComputationProgress

from elastichpc.base.platform.malleable import AllocationPort
from elastichpc.base.platform.malleable import QoSConfigurationPort
from elastichpc.base.platform.malleable import MalleablePlatformComponent

# Computation

# This is the process for the computation

def compute(computationProgress):
   for i in range(0,11):
      print "Calculando tarefa: " + str(i)
      computationProgress.value = i / 10.0
      time.sleep(5)

class MyReconfigurationPort(ReconfigurationPort):
   def updateResources(self, resources):
      print "updateResources: " + str(resources)

   def getComputationProgress(self):
      return self.component.computationProgress.value

class MyExecutionControlPort(ExecutionControlPort):
   def start(self, state = None):
      print "Iniciando Computacao..."
      allocationPort = self.component.services.getPort("AllocationPort")
      allocationPort.getResources()
      computation_process = Process(target = compute, args=(self.component.computationProgress,))
      computation_process.start();
      return

   def isFinished(self):
      if (self.component.computationProgress.value >= 1.0):
         return True
      return False

class MyMalleableComputation(MalleableComputationComponent):
   def __init__(self):
      super(MyMalleableComputation, self).__init__()
      self.computationProgress = Value('f', 0.0, lock = True)
      self.reconfigurationPort = MyReconfigurationPort("elastichpc.base.computation.malleable.ReconfigurationPort", self)
      self.executionControlPort = MyExecutionControlPort("elastichpc.base.computation.malleable.ExecutionControlPort", self)
      return

# Platform

# This is the process for the reconfiguration loop
def mape_k_loop(reconfiguration_port):
   progress = 0.0
   while progress < 1.0 :
      print "Recuperando Progresso da Computacao."
      reconfiguration_port.updateResources(resources = "Novos Recursos") 
      
      progress = reconfiguration_port.getComputationProgress() 
      print progress

      time.sleep(5)
   return

class MyAllocationPort(AllocationPort):
   def getResources(self):
      print "Enviando Recursos."
      reconfigurationPort = self.component.services.getPort("ComputationReconfigurationPort")
      mape_processo = Process(target = mape_k_loop, args=(reconfigurationPort,))
      mape_processo.start()
      print "Processo de Monitoramento Iniciado."
      return

class MyQoSConfigurationPort(QoSConfigurationPort):
   def setQoSContract(self, qos = None):
      print "Contrato Recebido."

class MyMalleablePlatform(MalleablePlatformComponent):
   def __init__(self):
      super(MyMalleablePlatform, self).__init__()
      self.allocationPort = MyAllocationPort("elastichpc.base.platform.malleable.AllocationPort", self)
      self.qosConfigurationPort = MyQoSConfigurationPort("elastichpc.base.platform.malleable.QoSConfigurationPort", self)
      return


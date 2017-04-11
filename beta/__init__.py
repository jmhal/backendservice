#-*- coding: iso-8859-15 -*-
import time
import logging
import random
from multiprocessing import Process, Value, Array

from elastichpc.base.computation.malleable import ReconfigurationPort
from elastichpc.base.computation.malleable import ExecutionControlPort
from elastichpc.base.computation.malleable import MalleableComputationComponent
from elastichpc.base.computation.malleable import ComputationProgress

from elastichpc.base.platform.malleable import AllocationPort
from elastichpc.base.platform.malleable import QoSConfigurationPort
from elastichpc.base.platform.malleable import MalleablePlatformComponent

# Computation

logger = logging.getLogger('root')

# This is the process for the computation

def compute(computationProgress, resources):
   interval = resources.value
   logger.debug("Iniciando Computação com Intervalo: " + str(interval))
   for i in range(0,11):
      logger.debug("Calculando tarefa: " + str(i))
      computationProgress.value = i / 10.0
      time.sleep(interval)

class MyReconfigurationPort(ReconfigurationPort):
   def updateResources(self, resources):
      logger.debug("updateResources: " + str(resources))
      self.component.computationResources.value = resources

   def getComputationProgress(self):
      return self.component.computationProgress.value

class MyExecutionControlPort(ExecutionControlPort):
   def start(self, state = None):
      logger.debug("Iniciando Computacao.")
      allocationPort = self.component.services.getPort("AllocationPort")
      resources =  allocationPort.getResources()
      self.component.computationResources.value = resources
      computation_process = Process(target = compute, args=(self.component.computationProgress,self.component.computationResources))
      computation_process.start();
      return

   def isFinished(self):
      if (self.component.computationProgress.value >= 1.0):
         return True
      return False

class MyMalleableComputation(MalleableComputationComponent):
   def __init__(self):
      super(MyMalleableComputation, self).__init__()

      # This is the sensor variable. It must be a primitive value.
      self.computationProgress = Value('f', 0.0, lock = True)

      # This is the parameter variable.
      # For this example will be a integer. But it my be an array (fixed size), a list, or a dictionnary (mutable, using managers).
      # Maybe for the final platform, the dictionnary will be the best option, since the key/value may contain 
      # different information models. 
      self.computationResources = Value('i', 0, lock = True)

      self.reconfigurationPort = MyReconfigurationPort("elastichpc.base.computation.malleable.ReconfigurationPort", self)
      self.executionControlPort = MyExecutionControlPort("elastichpc.base.computation.malleable.ExecutionControlPort", self)
      return

# Platform

# This is the process for the reconfiguration loop
def mape_k_loop(reconfiguration_port):
   progress = 0.0
   progressLog = {}
   while progress < 1.0 :
      logger.debug("Monitorando Progresso da Computação.")
      
      # Monitor
      progress = reconfiguration_port.getComputationProgress() 
      progressLog[time.time()] = progress
      logger.debug("Progresso: " + str(progress))

      # Analyze 
      if len(progressLog) >= 2 :
         firstTimeStamp = sorted(progressLog)[0]
         firstSample = progressLog[firstTimeStamp]

         lastTimeStamp = sorted(progressLog)[-1]
         lastSample = progressLog[lastTimeStamp]
      
         averageStepInterval = (lastTimeStamp - firstTimeStamp) / (lastSample - firstSample)
         logger.debug("Average Step Interval:" + str(averageStepInterval))

         predicted = (1.0 - lastSample) * averageStepInterval
         logger.debug("Predicted Remaining Time: " + str(predicted))

         # Plan

         # Execute
      else :
         logger.debug("Registros Insuficientes.")

      time.sleep(5)
   logger.debug(progressLog)
   return

class MyAllocationPort(AllocationPort):
   def getResources(self):
      interval = random.randint(1, 20)
      logger.debug("Enviando Recursos: " + str(interval))

      reconfigurationPort = self.component.services.getPort("ComputationReconfigurationPort")
      mape_processo = Process(target = mape_k_loop, args=(reconfigurationPort,))
      mape_processo.start()
      
      logger.debug("Processo de Monitoramento Iniciado.")
      return interval

class MyQoSConfigurationPort(QoSConfigurationPort):
   def setQoSContract(self, qos = None):
       logger.debug("Contrato Recebido.")
      
class MyMalleablePlatform(MalleablePlatformComponent):
   def __init__(self):
      super(MyMalleablePlatform, self).__init__()
      self.allocationPort = MyAllocationPort("elastichpc.base.platform.malleable.AllocationPort", self)
      self.qosConfigurationPort = MyQoSConfigurationPort("elastichpc.base.platform.malleable.QoSConfigurationPort", self)
      return


#-*- coding: iso-8859-15 -*-
import time
import logging
import random
from multiprocessing import Process, Value, Array, Pipe

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

def compute(compute_conn):
   while True:
   message = compute_conn.recv()
   if message[0] == "start":
   elif message[0] == "progress":
   elif message[0] == "resources":
   elif message[0] == "persist":
      continue
   elif message[0] == "stop":
      break
   compute_conn.close()
   
class MyReconfigurationPort(ReconfigurationPort):
   def updateResources(self, resources):
      logger.debug("Updating Resources for: " + str(resources))
      self.component.driver_conn.send(["resources", resources])
      message = self.component.driver_conn.recv()
      if message[0] == "resource_reply":
         return "SUCCESS"
      else 
         return "FAIL: " + message[1]

   def getComputationProgress(self):
      self.component.driver_conn.send(["progress"])
      message = self.component.driver_conn.recv()
      if message[0] == "progress_reply":
         return message[1]
      else:
         return -1.0

class MyExecutionControlPort(ExecutionControlPort):
   def start(self, state = None):
      logger.debug("Starting Computation.")
      allocationPort = self.component.services.getPort("AllocationPort")
      resources = allocationPort.getResources()

      computation_process = Process(target = compute, args=(self.component.compute_conn,))
      computation_process.daemon = True
      computation_process.start();

      self.component.driver_conn.send(["start", resources])
      return

   def isFinished(self):
      if (self.component.reconfigurationPort.getComputationProgress() >= 1.0):
         return True
      return False

class MyMalleableComputation(MalleableComputationComponent):
   def __init__(self):
      super(MyMalleableComputation, self).__init__()

      # There is a Pipe for the driver to communicate with the root unit
      driver_conn, compute_conn = Pipe()
      self.driver_conn = driver_conn
      self.compute_conn = compute_conn

      self.reconfigurationPort = MyReconfigurationPort("elastichpc.base.computation.malleable.ReconfigurationPort", self)
      self.executionControlPort = MyExecutionControlPort("elastichpc.base.computation.malleable.ExecutionControlPort", self)
      return

# Platform

# This is the process for the reconfiguration loop
def mape_k_loop(reconfiguration_port, qos_contract):
   # Initialize the execution record
   progress = 0.0
   progressLog = {}
   firstTimeStamp = time.time()
   firstSample = progress
   progressLog[firstTimeStamp] = progress
   lastTimeStamp = firstTimeStamp
   lastSample = firstSample

   while progress < 1.0 :
      logger.debug("Monitoring Computation Progress.")
      
      # Monitor
      progress = reconfiguration_port.getComputationProgress() 
      currentTimeStamp = time.time()
      currentSample = progress
      progressLog[currentTimeStamp] = currentSample
      logger.debug("Progress: " + ("{:.2f}".format(progress)))

      # Analyze 
      if currentSample > lastSample  :
    
         averageStepInterval = (currentTimeStamp - firstTimeStamp) / (currentSample * 10)
         logger.debug("Average Step Interval:" + ("{:.2f}".format(averageStepInterval)))

         # Plan
         predicted = 10 * (1.0 - currentSample) * averageStepInterval
         logger.debug("Predicted Remaining Time: " + ("{:.2f}".format(predicted)))
         reconfigurationAction = (False, 0)
         if qos_contract != None :
            executionTime = qos_contract["ExecutionTime"]
            executionCost = qos_contract["ExecutionCost"]
            elapsedTime = currentTimeStamp - firstTimeStamp
            # The case for increasing the resources
            if (elapsedTime + predicted) >  executionTime :
               targetAverageStepTime = (executionTime - elapsedTime) / ((1 - lastSample) * 10)
               reconfigurationAction = (True, targetAverageStepTime)
               logger.debug("Computation Must Be Reconfigured. New Resources: " + "{:.2f}".format(targetAverageStepTime))
            # The case for decreasing the resources   
            elif (elapsedTime + predicted) < executionTime: 

         # Execute
         if reconfigurationAction[0] == True:
            newResources = reconfigurationAction[1]
            reconfiguration_port.updateResources(newResources)

         # Update Samples
         lastTimeStamp = currentTimeStamp
         lastSample = currentSample
      
      else :
         logger.debug("Progress Unchanged.")

      time.sleep(5)
 
   elapsedTime = time.time() - firstTimeStamp

   logger.debug("Elapsed Time: " + "{:.2f}".format(elapsedTime))
   # logger.debug(progressLog)
   return

class MyAllocationPort(AllocationPort):
   def getResources(self):
      interval = random.randint(10, 20)
      logger.debug("Setting Resources: " + str(interval))

      reconfigurationPort = self.component.services.getPort("ComputationReconfigurationPort")
      qosContract = self.component.qosContract
      mape_processo = Process(target = mape_k_loop, args=(reconfigurationPort, qosContract))
      mape_processo.start()
      
      logger.debug("Monitoring Started.")
      return interval

class MyQoSConfigurationPort(QoSConfigurationPort):
   def setQoSContract(self, qos = None):
       if qos == None: 
          logger.debug("No Contract Defined.")
       else:
          logger.debug("Contract Defined (ExecutionTime, ExecutionCost): " + str(qos))
          self.component.qosContract = {}
          self.component.qosContract["ExecutionTime"] = qos[0]
          self.component.qosContract["ExecutionCost"] = qos[1]
      
class MyMalleablePlatform(MalleablePlatformComponent):
   def __init__(self):
      super(MyMalleablePlatform, self).__init__()
      self.qosContract = None 
      self.allocationPort = MyAllocationPort("elastichpc.base.platform.malleable.AllocationPort", self)
      self.qosConfigurationPort = MyQoSConfigurationPort("elastichpc.base.platform.malleable.QoSConfigurationPort", self)
      return


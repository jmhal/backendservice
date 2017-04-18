import CCAPython.gov.cca
import logging
import time
import collections

# Configure Logging
logger = logging.getLogger('root')

def mape_k_loop(reconfiguration_port, qos_contract, monitor_interval, sample_interval, reconfiguration_interval):
   """
   This is the method for the process running the monitoring loop.
   """

   # The progress is stored at a dictionary
   # The key is the timestamp when the variable was read.
   # The value is the computation progress at this timestamp.
   progress = 0.0
   progressLog = {}
   firstTimeStamp = time.time()
   firstSample = progress
   progressLog[firstTimeStamp] = progress
   lastTimeStamp = firstTimeStamp
   lastSample = firstSample

   # While the computation is not over
   while progress < 1.0 :
      logger.debug("Monitoring Computation Progress.")
      
      # Monitor
      progress = reconfiguration_port.getComputationProgress() 
      currentTimeStamp = time.time()
      currentSample = progress
      progressLog[currentTimeStamp] = currentSample
      logger.debug("Progress: " + ("{:.2f}".format(progress)))

      # Analyze 
      # Only run the analysis phase if there was progress made.
      if currentSample > lastSample :

         # Sort the progressLog by time stamp.
         # oldestSample will store the oldest progress recorded.
         # oldestTimeStamp will store the time stamp of the oldest progress recorded.
         orderedLogs = collections.OrderedDict(sorted(progressLog.items())).items() 
         numberOfSamples = len(orderedLogs)
         if numberOfSamples < sample_interval:
            # In this scenario, there is not enough samples in the interval, so we use the first sample
            oldestSample = firstSample
            oldestTimeStamp = firstTimeStamp
         else:
            # In this case, there is enough samples, so we take the last in the interval.
            oldestSample = orderedLogs[-(sample_interval)][1]
            oldestTimeStamp = orderedLogs[-(sample_interval)][0]

         # averageStepInterval is how much does it take to increase the progress in 0.1
         # currentTimeStamp is the time of the last progress verification
         # 
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

      # The Loop will sleep for monitor_interval seconds
      time.sleep(monitor_interval)
 
   elapsedTime = time.time() - firstTimeStamp

   logger.debug("Elapsed Time: " + "{:.2f}".format(elapsedTime))
   return


class AllocationPort(CCAPython.gov.cca.Port):
   def __init__(self, portType, component):    
      super(AllocationPort, self).__init__(portType)
      self.component = component
      return

   def getResources(self): 
      """
      This should return a resource description for the computation.
      This description should contain:
      - Number of nodes
      - Number of cores per node
      - Memory size per node
      - Hostname (for building the host file)
      """
      logger.debug("Setting Resources: " + str(self.component.resources))

      reconfigurationPort = self.component.services.getPort("ComputationReconfigurationPort")
      qosContract = self.component.qosContract
      mape_processo = Process(target = mape_k_loop, args=(reconfigurationPort, qosContract))
      mape_processo.start()
      
      logger.debug("Monitoring Started.")
      return self.component.resources


class QoSConfigurationPort(CCAPython.gov.cca.Port):
   def __init__(self, portType, component):
      super(QoSConfigurationPort, self).__init__(portType)
      self.component = component
      return

   def setQoSContract(self, resources = None, qos = None):
      """
      The contextual contract must be supplied by the computational system to the inner platform. 
      There are two sets of information:
      - The initial resource description. The Platform will use this description to instantiate 
      a self.resources attribute with the initial resources.
      - The QoS requirements dict. For malleable scenario, I'm considering:
        - Execution time estimative given the initial resources.
        - Execution cost restriction. 
        - Deviantion factor for the above restrictions.
        - A function, defined by the application provider or component developer, that, 
          given a new set of resources, delivers the new estimation of time and cost.
        {"execution_time" : 1342, "execution_cost" : 1000.0, "deviation_factor": 0.1,  "reconfiguration_function": function }
        The reconfiguration function should take as input:
        - Cluster Statistics (see base.platform.infrastructure.Cluster for formatting)
        - Computation Progress Log
        - Current Resources
        The output should be:
        - A new resource set to be allocated and sent to the Computation. (node_count, node_configuration)
      """
      raise NotImplementedError("Base Component.")

class MalleablePlatformComponent(CCAPython.gov.cca.Component):
   def __init__(self):
   
      # By default, there is no contract defined at component creation.
      # It must be set by the QoSConfigurationPort
      self.qosContract = None

      # By default, there is no resources set defined at component creation.
      # It must be set by the QoSConfigurationPort
      # The type of this object must be base.platform.infrastructure.Cluster
      self.resources = None
    
      self.allocationPort = AllocationPort("elastichpc.base.platform.malleable.AllocationPort", self)
      self.qosConfigurationPort = QoSConfigurationPort("elastichpc.base.platform.malleable.QoSConfigurationPort", self)
      return

   def setServices(self, services):
      self.services = services
      services.addProvidesPort(self.allocationPort, "AllocationPort", "elastichpc.base.platform.malleable.AllocationPort", None)
      services.addProvidesPort(self.qosConfigurationPort, "QoSConfigurationPort", "elastichpc.base.platform.malleable.QoSConfigurationPort", None)
      services.registerUsesPort("ComputationReconfigurationPort","elastichpc.base.computation.malleable.ReconfigurationPort", None)
      return

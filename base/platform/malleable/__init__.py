import CCAPython.gov.cca
import logging
import time
import collections

# Configure Logging
logger = logging.getLogger('root')

def mape_k_loop(platform_component, reconfiguration_port):
   """
   This is the method for the process running the monitoring loop.
   """

   # Extract Contract Information
   if platform_component.qos_contract != None:
      monitor_interval = platform_component.qos_contract["monitor_interval"]
      sample_interval = platform_component.qos_contract["sample_interval"]
      reconfiguration_interval = platform_component.qos_contract["reconfiguration_interval"]
      execution_time = platform_component.qos_contract["execution_time"]
      deviation_factor = platform_component.qos_contract["deviation_factor"]
      reconfiguration_function = platform_component.qos_contract["reconfiguration_function"]
   else:
      logger.debug("No QoS Contract!!!")
      return

   # The progress is stored at a dictionary
   # The key is the timestamp when the variable was read.
   # The value is the computation progress at this timestamp.
   progress = 0.0
   progress_log = {}
   first_time_stamp = time.time()
   last_reconfiguration = first_time_stamp
   first_sample = progress
   progress_log[first_time_stamp] = progress
   last_time_stamp = first_time_stamp
   last_sample = first_sample

   # While the computation is not over
   while progress < 1.0 :
      logger.debug("Monitoring Computation Progress.")
      
      # Monitor
      progress = reconfiguration_port.getComputationProgress() 
      current_time_stamp = time.time()
      current_sample = progress
      progress_log[current_time_stamp] = current_sample
      logger.debug("Progress: " + ("{:.2f}".format(progress)))

      # Analyze 
      # Only run the analysis phase if there was progress made.
      if current_sample > last_sample :

         # Sort the progress_log by time stamp.
         # oldest_sample will store the oldest progress recorded.
         # oldest_time_stamp will store the time stamp of the oldest progress recorded.
         ordered_logs = collections.OrderedDict(sorted(progress_log.items())).items() 
         number_of_samples = len(ordered_logs)
         if number_of_samples < sample_interval:
            # In this scenario, there is not enough samples in the interval, so we use the first sample
            oldest_sample = first_sample
            oldest_time_stamp = first_time_stamp
         else:
            # In this case, there is enough samples, so we take the last in the interval.
            oldest_sample = ordered_logs[-(sample_interval)][1]
            oldest_time_stamp = ordered_logs[-(sample_interval)][0]

         # average_step_interval is how much does it take to increase the progress in 0.1
         # current_time_stamp is the time of the last progress verification
         average_step_interval = (current_time_stamp - oldest_time_stamp) / ((current_sample - oldest_sample) * 10)
         logger.debug("Average Step Interval:" + ("{:.2f}".format(average_step_interval)))

         # Plan
         predicted_remaining_time = 10 * (1.0 - current_sample) * average_step_interval
         logger.debug("Predicted Remaining Time: " + ("{:.2f}".format(predicted_remaining_time)))
         reconfiguration_action = (False, 0)
         elapsed_time = current_time_stamp - first_time_stamp
         # The case for increasing the resources
         if (elapsed_time + predicted_remaining_time) > deviation_factor * execution_time :
	    new_resources = reconfiguration_function(platform_component, progress_log)
            reconfiguration_action = (True, new_resources) 
            logger.debug("Computation Must Be Reconfigured. New Resources: " + "{:.2f}".format(str(new_resources)))
         # The case for keeping the resources   
         elif (elapsed_time + predicted) < deviation_factor * executionTime: 
	    reconfiguration_action = (False, 0)

         # Execute
         if reconfiguration_action[0] == True and (current_time_stamp - last_reconfiguration > reconfiguration_interval):
            new_resources = reconfiguration_action[1]
            reconfiguration_port.updateResources(new_resources)
	    last_reconfiguration = current_time_stamp

         # Update Samples
         last_time_stamp = current_time_stamp
         last_sample = current_sample
      
      else :
         logger.debug("Progress Unchanged.")

      # The Loop will sleep for monitor_interval seconds
      time.sleep(monitor_interval)
 
   elapsed_time = time.time() - first_time_stamp

   logger.debug("Elapsed Time: " + "{:.2f}".format(elapsed_time))
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

      reconfiguration_port = self.component.services.getPort("ComputationReconfigurationPort")
      mape_process = Process(target = mape_k_loop, args=(self.component, reconfiguration_port))
      mape_process.daemon = True
      mape_process.start()
      
      logger.debug("Monitoring Started.")
      return self.component.resources


class QoSConfigurationPort(CCAPython.gov.cca.Port):
   def __init__(self, portType, component):
      super(QoSConfigurationPort, self).__init__(portType)
      self.component = component
      return

   def setQoSContract(self, resources = None, qos_contract = None):
      """
      The contextual contract must be supplied by the computational system to the inner platform. 
      There are two sets of information:
      - The initial resource description. The Platform will use this description to instantiate 
      a self.resources attribute with the initial resources.
      - The QoS requirements dict. For malleable scenario, I'm considering:
        - execution_time: execution time estimative given the initial resources.
        - execution_cost: execution cost restriction. 
        - deviation_factor: deviantion factor for the above restrictions.
        - monitor_interval: interval between two monitoring loops. 
        - sample_interval: how far back in the progress log should the analysis consider.
        - reconfiguration_interval: mininum interval between two reconfigurations.
        - reconfiguration_function: defined by the application provider or component developer, that, 
          given the contract, the cluster state and the progress log, return a new set of resources.
           The reconfiguration function should take as input:
           - Cluster Statistics (see base.platform.infrastructure.Cluster for formatting)
           - Computation Progress Log
           - Current Resources
          The output should be:
           - A new resource set to be allocated and sent to the Computation. (node_count, node_configuration)
      """
      self.component.resources = resources
      self.component.qos_contract = qos_contract
      return

class MalleablePlatformComponent(CCAPython.gov.cca.Component):
   def __init__(self):
   
      # By default, there is no contract defined at component creation.
      # It must be set by the QoSConfigurationPort
      self.qos_contract = None

      # By default, there is no resources set defined at component creation.
      # It must be set by the QoSConfigurationPort
      # The type of this object must be base.platform.infrastructure.Cluster
      self.resources = None
    
      self.allocation_port = AllocationPort("elastichpc.base.platform.malleable.AllocationPort", self)
      self.qosConfiguration_port = QoSConfigurationPort("elastichpc.base.platform.malleable.QoSConfigurationPort", self)
      return

   def setServices(self, services):
      self.services = services
      services.addProvidesPort(self.allocation_port, "AllocationPort", "elastichpc.base.platform.malleable.AllocationPort", None)
      services.addProvidesPort(self.qosConfiguration_port, "QoSConfigurationPort", "elastichpc.base.platform.malleable.QoSConfigurationPort", None)
      services.registerUsesPort("ComputationReconfigurationPort","elastichpc.base.computation.malleable.ReconfigurationPort", None)
      return

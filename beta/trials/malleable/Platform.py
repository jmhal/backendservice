import time
import logging
import collections
from infrastructure.resources.client import ResourcesProxy

def log(msg):
   logging.debug("PLATFORM: " + msg)
   return

def extrapolation(execution_log, compute_state):
   if (len(execution_log) == 0):
      return (0.0, 0.0)
   else:
      # predicting the execution time 
      start_time = execution_log.keys().sort()[0]
      current_time = time.time()
      predict_time = (current_time - start_time) / compute_state
      
      # predicting the execution cost
      cost = 0.0
      previous_vms = None
      previous_time = None
      for time_stamp in execution_log.keys().sort():
         if (previous_vms == None) and (previous == None):
	    previous_vms = execution_log[time_stamp]['nodes']
	    previous_time = time_stamp
	 else:
	    cost += (time_stamp - previous_time) * previous_vms
	    previous_time = time_stamp
	    previous_vms = execution_log[time_stamp]['nodes']
      cost += (predict_time - current_time) * previous_vms
      return (predict_time, cost)
      

def platform_unit(reconfiguration_port, url, stack_name, stack_id, qos_values, qos_weights, qos_factor, qos_intervals):
   # extract contract
   qos_values_dict = {}
   qos_values_dict['accuracy'] = float(qos_values.split(':')[0])
   qos_values_dict['execution_time'] = float(qos_values.split(':')[1])
   qos_values_dict['resource_efficiency'] = float(qos_values.split(':')[2])
   qos_values_dict['cost'] = float(qos_values.split(':')[3])
   qos_values_dict['power_consumption'] = float(qos_values.split(':')[4])
   log("QoS Values =" + str(qos_values_dict))

   qos_weights_dict = {}
   qos_weights_dict['accuracy'] = float(qos_weights.split(':')[0])
   qos_weights_dict['execution_time'] = float(qos_weights.split(':')[1])
   qos_weights_dict['resource_efficiency'] = float(qos_weights.split(':')[2])
   qos_weights_dict['cost'] = float(qos_weights.split(':')[3])
   qos_weights_dict['power_consumption'] = float(qos_weights.split(':')[4])
   log("QoS Weight =" + str(qos_weights_dict))

   alfa = float(qos_factor)
   log("QoS Factor =" + str(qos_factor))

   monitor_interval = int(qos_intervals.split(':')[0])
   sample_interval = int(qos_intervals.split(':')[1])
   reconfiguration_interval = int(qos_intervals.split(':')[2])
   log("Monitor Interval = " + str(monitor_interval))
   log("Sample Interval = " + str(sample_interval))
   log("Reconfiguration Interval = " + str(reconfiguration_interval))

   # create a proxy for resources control
   proxy = ResourcesProxy(url, stack_name, stack_id)
   log(url + ":" + stack_name + ":" + stack_id)

   # set up machinefile
   nodes = proxy.configure_machine_file()
   log("Number Of Nodes = " + str(nodes))

   # start the computation
   reconfiguration_port.get_actuator().value = "start"

   # execution log to keep track of the events
   execution_log = {}

   while reconfiguration_port.get_sensor().value < 1.0:
      # monitor interval
      time.sleep(monitor_interval)

      ## Monitoring Phase
      # retrieve computation state:
      #   computation progress 
      compute_state = reconfiguration_port.get_sensor().value

      # retrieve infrastructure state:
      #   efficiency
      resource_state = proxy.get_resource_state()

      ## Analysis Phase 

      # update resources
      if (compute_state > 0.2) and reconfigure:
         log("RECONFIGURATION BEFORE: " + str(nodes)) 
         reconfigure = False
         output = proxy.add_node(1)
	 with reconfiguration_port.machine_file_lock:
            nodes = proxy.configure_machine_file()
            log("RECONFIGURATION AFTER: " + str(nodes) + "|" + str(output)) 
 
      # insert state in log
      state = {'compute_state': compute_state, 'resource_state': resource_state, 'nodes': nodes}
      execution_log[time.time()] = state
      log("State = |" + str(state['compute_state']) + "|" + str(state['resource_state']) + "|" + str(state['nodes']) + "|")

   log("Finish Platform.")
   ordered_log = collections.OrderedDict(sorted(execution_log.items())).items() 
   log("Execution Log = " + str(ordered_log))

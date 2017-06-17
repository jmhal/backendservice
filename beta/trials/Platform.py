import time
import logging
from infrastructure.resources.client import ResourcesProxy

def log(msg):
   logging.debug("PLATFORM: " + msg)
   return

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
   log(url + ":" + stack_name + ":" + stack_id)
   proxy = ResourcesProxy(url, stack_name, stack_id)

   # set up machinefile
   nodes = proxy.configure_machine_file()
   log("Number Of Nodes = " + str(nodes))

   # start the computation
   reconfiguration_port.get_actuator().value = "start"

   # execution log to keep track of the events
   execution_log = {}

   while reconfiguration_port.get_actuator().value != "finished":
      # monitor interval
      time.sleep(5)

      # retrieve computation state:
      #   computation progress 
      compute_state = reconfiguration_port.get_sensor().value

      # retrieve infrastructure state:
      #   efficiency
      resource_state = proxy.get_resource_state()

      # update resources
      nodes = proxy.configure_machine_file()
 
      # insert state in log
      state = {'compute_state': compute_state, 'resource_state': resource_state, 'nodes': nodes}
      execution_log[time.time()] = state
      log ("State = " + str(state))

   log("Finish Platform.")

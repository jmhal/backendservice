import time
import logging
import collections
from infrastructure.resources.client import ResourcesProxy

def log(msg):
   logging.debug("PLATFORM: " + msg)
   return

def extrapolation(execution_log, compute_state):
   if (len(execution_log) == 0) or (float(compute_state) == 0):
      return (0.0, 0.0)
   else:
      # predicting the execution time
      start_time = sorted(execution_log.keys())[0]
      current_time = time.time()
      predicted_time = (current_time - start_time) / float(compute_state)
      
      # predicting the execution cost
      cost = 0.0
      previous_vms = None
      previous_time = None
      for time_stamp in sorted(execution_log.keys()):
         if (previous_vms == None) and (previous_time == None):
	    previous_vms = execution_log[time_stamp]['nodes']
	    previous_time = time_stamp
	 else:
	    cost += (time_stamp - previous_time) * previous_vms
	    previous_time = time_stamp
	    previous_vms = execution_log[time_stamp]['nodes']
      cost += (predicted_time - (current_time - start_time)) * previous_vms
      return (predicted_time, cost)
      

def platform_unit(reconfiguration_port, url, stack_name, stack_id, qos_values, qos_weights, qos_factor, qos_intervals):
   # extract contract
   qos_values_dict = {}
   qos_values_dict['accuracy'] = float(qos_values.split(':')[0])
   qos_values_dict['execution_time'] = float(qos_values.split(':')[1])
   qos_values_dict['efficiency'] = float(qos_values.split(':')[2])
   qos_values_dict['cost'] = float(qos_values.split(':')[3])
   qos_values_dict['power_consumption'] = float(qos_values.split(':')[4])
   log("QoS Values =" + str(qos_values_dict))

   qos_weights_dict = {}
   qos_weights_dict['accuracy'] = float(qos_weights.split(':')[0])
   qos_weights_dict['execution_time'] = float(qos_weights.split(':')[1])
   qos_weights_dict['efficiency'] = float(qos_weights.split(':')[2])
   qos_weights_dict['cost'] = float(qos_weights.split(':')[3])
   qos_weights_dict['power_consumption'] = float(qos_weights.split(':')[4])
   log("QoS Weight =" + str(qos_weights_dict))

   alpha = float(qos_factor)
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

   start_time = time.time()

   last_reconfiguration_time = time.time()

   last_compute_state = 0.0
 

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
      state = {'compute_state': compute_state, 'resource_state': resource_state, 'nodes': nodes}
      # log("State = " + str(state['compute_state']) + "|" + str(state['resource_state']) + "|" + str(state['nodes']) + "|")
      log("State = Elapsed Time : " + str(time.time() - start_time) + "; Progress : " + str(compute_state) + "; Efficiency : " + str(resource_state) + "; Nodes : " + str(nodes))

      if (len(execution_log) == 0) or (float(compute_state) == last_compute_state):
         log ("Not Enough Information for Analysis.")
         execution_log[time.time()] = state
         continue

      last_compute_state = float(compute_state)
      (predicted_time, predicted_cost) = extrapolation(execution_log, compute_state)
      log("(predicted_time, predicted_cost) = " + str(predicted_time) + "|" + str(predicted_cost))
 
      qos_sample = {}
      qos_sample['execution_time'] = predicted_time
      qos_sample['cost'] = predicted_cost

      load_average = 0.0 + float(resource_state.split('|')[0])
      for sample in execution_log.values():
         load_average += float(sample['resource_state'].split('|')[0])
      load_average /= len(execution_log) + 1	 
      qos_sample['efficiency'] = load_average
     
      log("QoS Sample = " + str(qos_sample))

      ## Planning Phase
      breach = False
      delta = {}
      #for param in qos_values_dict.keys():
      for param in ["execution_time", "cost", "efficiency"]:
         if not ((qos_sample[param] > (1 - alpha) * qos_values_dict[param]) and (qos_sample[param] < (1 + alpha) *qos_values_dict[param])):
            delta[param] = abs(qos_values_dict[param] - qos_sample[param]) 
	    delta[param] /= qos_values_dict[param]
	    delta[param] *= qos_weights_dict[param]
	    breach = True
      
      if not breach:
         log("Contract not breached =" + str(delta))
	 state = {'compute_state': compute_state, 'resource_state': resource_state, 'nodes': nodes}
         execution_log[time.time()] = state
         # log("State = |" + str(state['compute_state']) + "|" + str(state['resource_state']) + "|" + str(state['nodes']) + "|")
         log("State = Elapsed Time : " + str(time.time() - start_time) + "; Progress : " + str(compute_state) + "; Efficiency : " + str(resource_state) + "; Nodes : " + str(nodes))
         continue
      else:
         log("Contract breached = " + str(delta))
	   
      maxValue = 0.0
      maxParam = None
      for param in delta.keys():
         if delta[param] > maxValue :
	    maxParam = param
	    maxValue = delta[param]
      log("Parameter to Reconfigure: " + maxParam)

      N = 0
      if maxParam in ["efficiency"]:
         if qos_sample[maxParam] < (1 - alpha) * qos_values_dict[maxParam]:
	    # scale down
	    N = -1
	    log("Scale Down = " + maxParam + "|" + str(qos_sample[maxParam]) + "|" + str(qos_values_dict[maxParam]))
	 elif qos_sample[maxParam] > (1 + alpha) * qos_values_dict[maxParam]:
	    # scale up
	    N = 1
	    log("Scale Up = " + maxParam + "|" + str(qos_sample[maxParam]) + "|" + str(qos_values_dict[maxParam]))
      elif maxParam in ["execution_time"]:
         if qos_sample[maxParam] < (1 - alpha) * qos_values_dict[maxParam]:
	    # scale down
	    N = -1
	    log("Scale Down = " + maxParam + "|" + str(qos_sample[maxParam]) + "|" + str(qos_values_dict[maxParam]))
	 elif qos_sample[maxParam] > (1 + alpha) * qos_values_dict[maxParam]:
	    # scale up
	    N = 1
	    log("Scale Up = " + maxParam + "|" + str(qos_sample[maxParam]) + "|" + str(qos_values_dict[maxParam]))
      elif maxParam in ["cost"]:
         if qos_sample[maxParam] < (1 - alpha) * qos_values_dict[maxParam]:
	    # scale down
	    N = 1
	    log("Scale Up = " + maxParam + "|" + str(qos_sample[maxParam]) + "|" + str(qos_values_dict[maxParam]))
	 elif qos_sample[maxParam] > (1 + alpha) * qos_values_dict[maxParam]:
	    # scale up
	    N = -1
	    log("Scale Down = " + maxParam + "|" + str(qos_sample[maxParam]) + "|" + str(qos_values_dict[maxParam]))

           
      log("N Value =" + str(N))
      ## Execution Phase
      if reconfiguration_port.get_actuator().value == "finished":
         log("Computation is over. Forget Scaling.")
         break
      if (time.time() - last_reconfiguration_time) > reconfiguration_interval:
         log("RECONFIGURATION BEFORE: " + str(nodes)) 
         if N == 1:
            # No problem, does not affect running computation
           output = proxy.add_node(1)
         elif N == -1:
            # We cannot remove a node while computation is using it
            if (nodes == 2):
               log ("Contract down limit reached. Skipping Scale Down.")
               continue 
            reconfiguration_port.get_actuator().value = "scale_down"
            while (reconfiguration_port.get_actuator().value == "scale_down"):
               log("Waiting to Scale Down.")
               state = {'compute_state': compute_state, 'resource_state': resource_state, 'nodes': nodes}
               execution_log[time.time()] = state
               # log("State = |" + str(state['compute_state']) + "|" + str(state['resource_state']) + "|" + str(state['nodes']) + "|")
               log("State = Elapsed Time : " + str(time.time() - start_time) + "; Progress : " + str(compute_state) + "; Efficiency : " + str(resource_state) + "; Nodes : " + str(nodes))
               time.sleep(monitor_interval)
            if reconfiguration_port.get_actuator().value == "go_ahead":
               log("Ready to Scale Down.")
               output = proxy.remove_node(1)
               reconfiguration_port.get_actuator().value = "scaled"
               log("Scaled Down.")
            else :
               log("Why Here? " + reconfiguration_port.get_actuator().value)
	 with reconfiguration_port.machine_file_lock:
	    nodes = proxy.configure_machine_file()
         log("RECONFIGURATION AFTER: " + str(nodes) + "|" + str(output))
	 last_reconfiguration_time = time.time() 
      else:
         log("RECONFIGURATION INTERVAL NOT DONE.")
      
      # insert state in log
      state = {'compute_state': compute_state, 'resource_state': resource_state, 'nodes': nodes}
      execution_log[time.time()] = state
      # log("State = |" + str(state['compute_state']) + "|" + str(state['resource_state']) + "|" + str(state['nodes']) + "|")
      log("State = Elapsed Time : " + str(time.time() - start_time) + "; Progress : " + str(compute_state) + "; Efficiency : " + str(resource_state) + "; Nodes : " + str(nodes))

   log("Finish Platform.")
   ordered_log = collections.OrderedDict(sorted(execution_log.items())).items() 
   start_time = ordered_log[0][0]
   end_time = ordered_log[-1][0]
   log("Elapsed = " + str(end_time - start_time))
   log("Execution Log = " + str(ordered_log))

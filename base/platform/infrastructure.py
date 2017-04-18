"""
As basic infrastructure, we consider a cluster. This class is abstract. 
In the final scenario, a maintainer should derive these classes to represent its real infrastructure.
"""

class Cluster: 
   """
   This is a cluster infrastructure. It represents the resources available to the computational system. 
   """
   def __init__(self):
      """
      The extended class must initialize the set of nodes for the cluster.
      There are several options. The maintainer may hard code the configuration or
      keep it in a configuration file.
      Another task is to set the credentials for the cluster.
      """
      raise NotImplementedError("Abstract Class!")

   def getNodes(self):
      """
      Returns the nodes, as a dictionary, {hostname : NodeObject}
      """
      raise NotImplementedError("Abstract Class!")

   def isElastic(self):
      """
      Returns True if the cluster supports horizontal elasticity, False otherwise.
      """
      raise NotImplementedError("Abstract Class!")

   def getClusterStatistics(self):
      """
      Returns the overall status of the cluster. 
      For the CPU, Memory, Disk and Bandwidth, is the average for the values of each node.
      For the cost, is the sum of the value of each node. 
      sample output: {"cpuload": 0.5, "memory" : 0.5, "diskusage": 0.5, "network" : 0.5, "cost" : 13.4 }
      """
      raise NotImplementedError("Abstract Class!")
  
   def addNode(self)
      """  
      Add a node to the set of resources.      
      The node is added with the default values from the contract.
      It may be reconfigured right after.
      """
      raise NotImplementedError("Abstract Class!")

   def removeNode(self, hostname)
      """
      Remove a node from the set of resources.
      """
      raise NotImplementedError("Abstract Class!")

class Node:
   """
   Every cluster is made of nodes. 
   There is no need for detailed description of the node, since the contextual
   contract guarantees that it has the necessary settings.
   """
   def __init__(self)
      """
      The maintaner must extend this class with at least the following attributes:
      - min_core_count
      - max_core_count
      - current_core_count
      - min_memory
      - max_memory
      - current_memory
      - network_bandwidth
      - hostname 
      - credentials
      - a cost function (current_core_count, current_memory, etc) -> cost_per_hour
      - accumulated_cost
      - creation_time
      - last_reconfiguration_time
      """
      raise NotImplementedError("Abstract Class!")

   def isElastic(self):
      """
      Returns True if the node supports vertical elasticity, False otherwise.
      """
      raise NotImplementedError("Abstract Class!")

   def reconfigureNode(self, new_configuration):
      """
      Configure the new values for current_core_count and current_memory, and for each configurable parameter.
      new_configuration = { "core_count" : 4, "memory" : 16000 }
      """
      raise NotImplementedError("Abstract Class!")

   def getStatistics(self):
      """
      The metrics/values for this node type.
      Each performance metric has value in the interval [0.0 ... 1.0]

      CPU: third field of /proc/loadavg divided by core count.
      Memory: second column of free -m divided by total memory.
      Disk: fourth column of df -h for the /home partition row.
      Network Metric: total traffic from uptime (RX + TX bytes) divided by the uptime and the network bandwidth. 
      By default, the metrics are collected instantaneously. But the platform manager may collect this information
      from monitoring systems such as Ganglia. 
      
      The cost metric contains the total amount spent during execution for this node.

      sample output: {"cpuload": 0.5, "memory" : 0.5, "diskusage": 0.5, "network" : 0.5, "cost" : 13.4 }
      """
      raise NotImplementedError("Abstract Class!")


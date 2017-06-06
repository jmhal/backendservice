"""
As basic infrastructure, we consider a cluster. This class is abstract. 
In the final scenario, a maintainer should derive these classes to represent its real infrastructure.
"""

class Cluster: 
   """
   This is a cluster infrastructure. It represents the resources available to the computational system. 
   """
   def __init__(self, credentials, profile):
      """
      The extended class must initialize the set of nodes for the cluster.
      There are several options. The maintainer may hard code the configuration or
      keep it in a configuration file.
      Another task is to set the credentials for the cluster.
      """
      self.profile = profile
      raise NotImplementedError("Abstract Class!")

   def getResources(self):
      """
      Returns the nodes, as a machine file for MPI
      node0:corecount
      node1:corecount
      node2:corecount
      ...
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
  
   def addNode(self, n = 1)
      """  
      Add a node to the set of resources.      
      The node is added with the default values from the contract.
      It may be reconfigured right after.
      """
      raise NotImplementedError("Abstract Class!")

   def removeNode(self, n = 1)
      """
      Remove a node from the set of resources.
      """
      raise NotImplementedError("Abstract Class!")


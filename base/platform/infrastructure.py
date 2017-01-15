"""
As basic infrastructure, we consider a cluster, that might be virtual or physical.
These classes are abstract. In the final scenario, a maintainer should derive these
classes to represent it's real infrastructure.
"""

"""
This is a cluster infrastructure. It represents the whole infrastructure available
to the computational system. 
- If it is a virtual Cluster, nodes may be added. Also, elasticity may change the configuration of these nodes and the assignment of nodes to components. 
- If it is a physical cluster, we cannot alter the nodes' configuration.
"""
class Cluster: 
   def __init__(self):
      """
      The extended class must initialize the set of nodes for the cluster.
      There are several options. The maintainer may hard code the configuration or
      keep it in a configuration file.
      Another task is to set the credentials for the cluster.
      """
      raise NotImplementedError("Abstract Class!")

   def isVirtual(self):
      """
      Should return True if this cluster
      """
      raise NotImplementedError("Abstract Class!")

   def getNodes(self):
      """
      Returns the nodes, as a dictionnary, {NodeID: NodeObject}
      """
      raise NotImplementedError("Abstract Class!")

   def getNodesForComponent(self, componentId):
      """
      Returns the nodes assigned to a component.
      We consider that a node is assigned to a single component.
      """
      raise NotImplementedError("Abstract Class!")

   def assignNodeForComponent(self, nodeId, componentId):
      """
      Establishes that node with nodeId is assigned to component componentId
      """
      raise NotImplementedError("Abstract Class!")

   def deAssignNodeForComponent(self, nodeId, componentId):
      """
      Establishes that node with nodeId is no longer assigned to component componentId
      """
      raise NotImplementedError("Abstract Class!")

   def getClusterStatistics(self):
      """
      Returns the overall status of the cluster. I expect the format to be similar with
      a dictionary created from a YAML file. In other words, key:value, where key stands
      for a metric (cluster load, bandwidth usage, etc) and value is the perception for that
      metric. 
      The metrics and values are defined by the maintainer developing the Platform component and
      must be informed in the contextual contract for the platform.
      For example, a Virtual Cluster may inform the price of spot instances. Another possibility is
      a accounting of how much the execution of each component is costing the user.
      """
      raise NotImplementedError("Abstract Class!")
  
   def getNodeStatistics(self, nodeId):
      """
      Returns the status of a specific node. The same way as getClusterStatistics, I expect
      this to be highly implementation dependent. 
      """
      raise NotImplementedError("Abstract Class!")

class VirtualCluster(Cluster):
   def __init__(self):
      """ 
      This class should be extended to acommodate the different cloud providers
      """
      raise NotImplementedError("Abstract Class!")

   def addNode(self, flavorId):
      """  
      As a virtual cluster, you can create new instances of virtual machines.
      """
      raise NotImplementedError("Abstract Class!")

   def removeNode(self, nodeId):
      """
      As a virtual cluster, you can remove instances of virtual machines.
      """
      raise NotImplementedError("Abstract Class!")

   def resizeNode(self, newConfiguration):
      """
      This is tricky method. After, not all hypervisors support vertical elasticity.
      If a maintainer has a hypervisor with such feature, it must define a configuration
      object to describe how to change the node. For example, the configuration object may 
      have scalar quantities for memory and storage. Will it require rebooting the node?
      I don't know. This method is here in case future advances allow easier vertical elasticity.
      """
      raise NotImplementedError("Abstract Class!")

class PhysicalCluster(Cluster):
   def __init__(self):
      """
      I don't think that the Physical Cluster has any special methods.
      """
      raise NotImplementedError("Abstract Class!")

"""
Every cluster is made of nodes. We assume a homogeneous in certain aspects, for example, 
processor architecture.
"""
class Node:
   def __init__(self):
      """
      The extended class must have attributes to describing the node configuration.
      For example, CPU, Memory, Storage, etc.
      They must match the cluster description.
      """
      raise NotImplementedError("Abstract Class!")

   def getStatistics(self):
      """
      The metrics/values for this node type.
      """
      raise NotImplementedError("Abstract Class!")



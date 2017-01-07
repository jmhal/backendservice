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
      """
      raise NotImplementedError("Abstract Class!")

   def isVirtual(self):
      """
      Should return True if this cluster
      """
      raise NotImplementedError("Abstract Class!")

   def getNodes(self):
      """
      Return the nodes, as a dictionnary, {NodeID: NodeObject}
      """
      raise NotImplementedError("Abstract Class!")

class VirtualCluster(Cluster):
   def __init__(self):
      raise NotImplementedError("Abstract Class!")

   def addNode(self, flavor):
      raise NotImplementedError("Abstract Class!")

   def removeNode(self, nodeId):
      raise NotImplementedError("Abstract Class!")

class PhysicalCluster(Cluster):
   def __init__(self):
      raise NotImplementedError("Abstract Class!")

"""
Every cluster is made of nodes. We assume a homogeneous in certain aspects, for example, 
processor architecture.
"""
class Node:
   def __init__(self):
      raise NotImplementedError("Abstract Class!")


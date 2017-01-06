
"""
This is an Abstract Class for all infrastructures.
"""
class Infrastructure(object):
   def __init__(self):
      raise NotImplementedError("Abstract Class!")

class ComputingResource(object):
   def __init__(self):
      raise NotImplementedError("Abstract Class!")
   

"""
This is a cluster infrastructure. 
"""
class Cluster(Infrastructure): 
   def __init__(self):

   def isVirtual(self):

   def addNodes(self, N):

   def removeNodes(self, N):


   def removeNode(self):

   def updateNodeConfiguration(self, memory, cores, storage):



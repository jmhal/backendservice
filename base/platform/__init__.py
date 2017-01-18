import gov.cca

# The component ports

## Provides ports

### Activation 
class ActivationPort(gov.cca.Port):
   def addNodes(self, componentID, flavorID, numberOfNodes = 1):
      """
      Will add nodes with flavorID configuration to component identified by componentID.
      After the allocation, this will trigger the invocation of a method on the Notification port
      of the Computation component. 
      """
      pass

   def removeNodes(self, componentID, nodeID, numberOfNodes = 1)
      """ 
      Will remove nodes from component identified by componentID.
      The deallocation should be preceded by invocation of a method on the Notification port of
      the Computation component.
      """
      pass
   
   def resizeNode(self, componentID, nodeID, newConfiguration):
      """
      This is for vertical elasticity. The newConfiguration should contain the changes in the
      NumberOfCores/Memory/Disk Space. These dimensions are not strict. For example, one could
      envision changing the power consumption of the processor. 
      The resize should be preceded by invocation of a method on the Notification port of
      the Computation component.
      """
      pass

   def persistComputation(self, componentID):
      """
      This will persist the current state of the computation for a component, then return a endpoint
      for this saved state. For a cloud, the endpoint might be the URI of a snapshot.
      The persist will invoke methods on the Notification port of the Computation Component.
      """
      pass

   def startComputation(self, componentID, state=None):
      """
      Invokes the go port for the Computation component. If previous state is provided, the platform
      will distributed the data accordingly among the allocated nodes.

      """
      pass

### Monitoring
class MonitoringPort(gov.cca.Port):
   def getNodeState(self, nodeID:
      """
      Will get the metrics for the node identified by nodeID
      """
      pass
  
   def getClusterState(self):
      """
      A complete summary of the cluster metrics.
      """
      pass

   def getComponentToResourceMapping(self):
      """
      A mapping describing which resources each component is associated.
      """
      pass

### Allocation
class AllocationPort(gov.cca.Port):
   def allocateResources(self, componentID, resourceDescription):
      """
      This port is used by the component to require the initial resources.
      """
      pass

   def deAllocateResources(self, componentID):
      """
      This port is used by the component to release resources.
      """
      pass

## Uses ports

### Notification
class NotificationPort(gov.cca.Port):
   pass

# The component itself
class PlatformComponent(gov.cca.Component):
   def __init__(self):
      self.activationPort = ActivationPort("elastichpc.base.platform.ActivationPort")

   def setServices(self, services):
      self.services = services
      self.addProvidesPort(self.activationPort, "ActivationPort", "elastichpc.base.platform.ActivationPort")

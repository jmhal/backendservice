import gov.cca

class ReconfigurationDecisionLoop():
   def __init__(self, reconfigurationPort):
      self.reconfigurationPort = reconfigurationPort
      return

   def monitor(self):
      raise NotImplementedError("Base Component.")

   def analysis(self):
      raise NotImplementedError("Base Component.")

   def planning(self):
      raise NotImplementedError("Base Component.")

   def execute(self):
      raise NotImplementedError("Base Component.")

class AllocationPort(gov.cca.Port):
   def __init__(self, portType):    
      super(AllocationPort, self). __init__(portType)
      return

   def getResources(): 
      """
      This should return a resource description for the computation.
      This description should contain:
      - Number of nodes
      - Number of cores per node
      - Memory size per node
      - IP adress of each node (for building the host file)
      """
      raise NotImplementedError("Base Component.")

class QoSConfigurationPort(gov.cca.Port):
   def __init__(self, portType):
      super(AllocationPort, self). __init__(portType)
      return

   def setQoSContract(self, qos):
      raise NotImplementedError("Base Component.")

class MalleablePlatformComponent(gov.cca.Component):
   def __init__(self):
      self.allocationPort = AllocationPort("elastichpc.base.platform.malleable.AllocationPort")
      self.qosConfigurationPort = QoSConfigurationPort("elastichpc.base.platforma.malleable.QoSConfigurationPort")
      return

   def setServices(self, services):
      self.services = services
      services.addProvidesPort(self.allocationPort, "AllocationPort", "elastichpc.base.platform.malleable.AllocationPort", None)
      services.addProvidesPort(self.allocationPort, "QosConfigurationPort", "elastichpc.base.platform.malleable.QosConfigurationPort", None)
      services.registerUsesPort("ComputationReconfiguration","elastichpc.base.computation.malleable.ReconfigurationPort", None)
      return

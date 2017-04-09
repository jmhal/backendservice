import CCAPython.gov.cca

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

class AllocationPort(CCAPython.gov.cca.Port):
   def __init__(self, portType, component):    
      super(AllocationPort, self).__init__(portType)
      self.component = component
      return

   def getResources(self): 
      """
      This should return a resource description for the computation.
      This description should contain:
      - Number of nodes
      - Number of cores per node
      - Memory size per node
      - IP adress of each node (for building the host file)
      """
      raise NotImplementedError("Base Component.")

class QoSConfigurationPort(CCAPython.gov.cca.Port):
   def __init__(self, portType, component):
      super(QoSConfigurationPort, self).__init__(portType)
      self.component = component
      return

   def setQoSContract(self, qos):
      """
      This should represent the execution requirements. 
      For malleable scenario, I'm considering:
      - Execution time estimative given the initial resources.
      - Execution cost restriction. 
      - A function, defined by the application provider or component developer, that, 
        given a new set of resources, delivers the new estimation of time and cost.
      """
      raise NotImplementedError("Base Component.")

class MalleablePlatformComponent(CCAPython.gov.cca.Component):
   def __init__(self):
      self.allocationPort = AllocationPort("elastichpc.base.platform.malleable.AllocationPort", self)
      self.qosConfigurationPort = QoSConfigurationPort("elastichpc.base.platform.malleable.QoSConfigurationPort", self)
      return

   def setServices(self, services):
      self.services = services
      services.addProvidesPort(self.allocationPort, "AllocationPort", "elastichpc.base.platform.malleable.AllocationPort", None)
      services.addProvidesPort(self.qosConfigurationPort, "QoSConfigurationPort", "elastichpc.base.platform.malleable.QoSConfigurationPort", None)
      services.registerUsesPort("ComputationReconfigurationPort","elastichpc.base.computation.malleable.ReconfigurationPort", None)
      return

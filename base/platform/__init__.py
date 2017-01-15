import gov.cca

# The component ports

## Provides ports

### Activation 
class ActivationPort(gov.cca.Port):
   pass

### Monitoring
class MonitoringPort(gov.cca.Port):
   pass

### Allocation
class AllocationPort(gov.cca.Port):
   pass

## Uses ports

### Notification
class NotificationPort(gov.cca.Port):
   pass

# The component itself
class PlatformComponent(gov.cca.Component):
   def __init__(self):
      slef.activationPort = BaseActivationPort("elastichpc.base.platform.ActivationPort")
   def setServices(self, services):
      self.services = services
      self.addProvidesPort(self.activationPort, "ActivationPort", "elastichpc.base.platform.ActivationPort")

#!/usr/bin/python
import time
from CCAPython.framework.manage.builders import FrameworkHandle
from CCAPython import gov

if __name__ == '__main__':
   fwk = FrameworkHandle()

   computation = fwk.createInstance("ComputationInstance", "elastichpc.beta.MyMalleableComputation", None)
   platform = fwk.createInstance("PlatformInstance", "elastichpc.beta.MyMalleablePlatform", None)

   fwk.connect(computation, "AllocationPort", platform, "AllocationPort")
   fwk.connect(platform, "ComputationReconfigurationPort", computation, "ComputationReconfigurationPort")

   qosPort = fwk.lookupPort(platform, "QoSConfigurationPort")
   qosPort.setQoSContract()

   executionPort = fwk.lookupPort(computation, "ExecutionControlPort")
   executionPort.start()

   while executionPort.isFinished() == False: 
      print "Componentes ainda executando..."
      time.sleep(5)

   fwk.destroyInstance(computation, 0.0)
   fwk.destroyInstance(platform, 0.0)
    

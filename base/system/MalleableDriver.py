#!/usr/bin/python

import time
from framework.manage.builders import FrameworkHandle

if __name__ == '__main__':
   fwk = FrameworkHandle()

   computation = fwk.createInstance("ComputationInstance", "elastichpc.base.computation.malleable.MalleableComputationComponent", None)
   platform = fwk.createInstance("PlatformInstance", "elastichpc.base.platform.malleable.MalleablePlatformComponent", None)

   fwk.connect(computation, "AllocationPort", platform, "AllocationPort")
   fwk.connect(platform, "ComputationReconfigurationPort", computation, "ComputationReconfigurationPort")

   qosPort = fwk.lookupPort(platform, "QoSConfigurationPort")
   qosPort.setQosContract()

   executionPort = fwk.lookupPort(computation, "ExecutionControlPort")
   executionPort.start(state = None)

   while (executionPort.isFinished == False):
      time.sleep(60)

   fwk.destroyInstance(computation, 0.0)
   fwk.destroyInstance(platforma, 0.0)

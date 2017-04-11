#!/usr/bin/python
#-*- coding: iso-8859-15 -*-
import time
import log
from CCAPython.framework.manage.builders import FrameworkHandle
from CCAPython import gov

logger = log.setup_custom_logger('root')

if __name__ == '__main__':
   logger.debug("Criando o Framework.")
   fwk = FrameworkHandle()

   logger.debug("Criando os Componentes.")
   computation = fwk.createInstance("ComputationInstance", "elastichpc.beta.MyMalleableComputation", None)
   platform = fwk.createInstance("PlatformInstance", "elastichpc.beta.MyMalleablePlatform", None)

   logger.debug("Conectando as Portas.")
   fwk.connect(computation, "AllocationPort", platform, "AllocationPort")
   fwk.connect(platform, "ComputationReconfigurationPort", computation, "ComputationReconfigurationPort")

   logger.debug("Configurando o Contrato.")
   qosPort = fwk.lookupPort(platform, "QoSConfigurationPort")
   qosPort.setQoSContract()

   logger.debug("Iniciando a Execução da Computação")
   executionPort = fwk.lookupPort(computation, "ExecutionControlPort")
   executionPort.start()

   while executionPort.isFinished() == False: 
#      logger.debug("Computação em Execução.")
      time.sleep(5)

   fwk.destroyInstance(computation, 0.0)
   fwk.destroyInstance(platform, 0.0)
    

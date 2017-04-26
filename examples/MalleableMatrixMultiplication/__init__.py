import os
import CCAPython.gov.cca
import elastichpc.base.computation.malleable.MalleableComputationComponent
import elastichpc.base.computation.malleable.ComputationUnitImpl

from elastichpc import logging

# Setting Up Log
logger = logging.getLogger('root')

class MatrixMultiplicationWorkQueue(base.computation.malleable.ComputationUnitImpl):
   """
   Controls the MPI process creation.
   """
   def __init__(self):
      raise NotImplementedError("Interface.")
     
   def start(self, resources, input_data):
      raise NotImplementedError("Interface.")

   def getProgress(self, new_resources):
      raise NotImplementedError("Interface.")

   def updateResources(self, new_resources):
      raise NotImplementedError("Interface.")
    
   def persist(self):
      raise NotImplementedError("Interface.")

   def getResults(self):
      raise NotImplementedError("Interface.")

   def stop(self):
      raise NotImplementedError("Interface.")


class MatrixSetup(CCAPython.gov.cca.Port):
   """
   Environment Port
   """
   def __init__(self, portType, component):
      self.component = component
      super(MatrixSetup, self).__init__(portType)

   def setMatrixFileNames(self, matrix_A_filename, matrix_B_filename, matrix_C_filename): 
      logger.debug("Matrix A %s, Matrix B %s, Matrix %s" % (matrix_A_filename, matrix_B_filename, matrix_C_filename))
      if os.path.isfile(matrix_A_filename) and os.path.isfile(matrix_B_filename) and os.path.isfile(matrix_C_filename): 
         self.component.matrix_A_filename = matrix_A_filename
         self.component.matrix_B_filename = matrix_B_filename
         self.component.matrix_C_filename = matrix_C_filename
         self.component.matrix_set = True
         return True
      else:
         return False

class MatrixMultiplication(CCAPython.gov.cca.Port):
   """
   Task Port
   """
   def __init__(self, portType, component):
      self.component = component
      super(MatrixMultiplication, self).__init__(portType)

   def matrixMultiplication():
      pass

class MatrixMultiplicationComponent(base.computation.malleable.MalleableComputationComponent):
   def __init__(self):
      super(MatrixMultiplicationComponent, self).__init__()
      self.computation_impl = MatrixMultiplicationWorkQueue()
      self.matrix_set = False
      self.matrix_setup_environment_port = MatrixSetup("elastichpc.examples.MalleableMatrixMultiplication.MatrixSetup", self)
      self.matrix_multiplication_task_port = MatrixSetup("elastichpc.examples.MalleableMatrixMultiplication.MatrixMultiplication", self)
      return

   def setServices(self, services):
      super(MatrixMultiplicationComponent, self).setServices(services)
      services.addProvidesPort(self.matrix_setup_environment_port, "MatrixSetup", "elastichpc.examples.MalleableMatrixMultiplication.MatrixSetup", None)
      services.addProvidesPort(self.matrix_multiplication_task_port, "MatrixMultiplication", "elastichpc.examples.MalleableMatrixMultiplication.MatrixMultiplication", None)
      return



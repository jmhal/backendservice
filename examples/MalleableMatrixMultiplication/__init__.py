import os
import subprocess
import zmq
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
   def __init__(self, component):
      self.component = component
      self.last_line = -1
      return      
     
   def start(self, resources, input_data):
      """
      Creates the subprocess for running the MPI computation.
      """
      self.input_data = input_data
      command = ["mpirun", "-n", str(self.parse_resources(resources)) , "./Matrix_Work_Queue.py"] + input_data + [str(self.last_line)]
      self.process = subprocess.Popen(command, stdout = subprocess.PIPE, stderr=subprocess.STDOUT)  

      context = zmq.Context()
      self.socket = context.socket(zmq.REQ)
      self.socket.connect("tcp://localhost:33002")
      return True

   def getProgress(self):
      self.socket.send("progress")
      progress = float(self.socket.recv())
      logger.debug("Matrix Multiplication Work Queue Progress: %.2f" % progress)
      return progress

   def updateResources(self, new_resources):
      """
      Persist the computation, set the new last line, and restart the process.
      """
      self.persist()
      return self.start(new_resources, self.input_data)
      
   def persist(self):
      """
      Persist will stop the computation, but it will return the last line computed for the resulting matrix. 
      """
      self.socket.send("persist")
      self.last_line = int(self.socket.recv())
      self.socket.close()
      logger.debug("Matrix Multiplication Work Queue Persist Last Line: %d" % self.last_line)
      return self.last_line
 
   def getResults(self):
      return self.input_data[2] 

   def stop(self):
      """
      Stops the computation and log the output.
      """
      self.process.terminate()
      (stdout, stderr) = self.process.communicate()
      logger.debug("Computation Stopped: %s %s" % (stdout, stderr))
      return True

   def parse_resources(self, resources):
      """
      Here, I'm defining that for this particular component, the resources arrive as a list with this format;
      resources = [ ("node0", 2), ("node1", 2), ("node2", 2), ("node3", 2)]
      A list of tuples, the first item the hostname or IP, the second item the number of cores or CPUs.
      """
      number_of_processes = 1
      for host in resources:
         number_of_processes += host[1]

      logger.debug("Number of processes is: " + number_of_processes)
      return number_of_processes

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
         self.component.input_data.append(matrix_A_filename)
         self.component.input_data.append(matrix_B_filename)
         self.component.input_data.append(matrix_C_filename)
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
      
      self.computation_impl = MatrixMultiplicationWorkQueue(self)
      # For this component, the input_data is a list that is appended to the command starting the MPI process.
      self.input_data = []

      self.matrix_setup_environment_port = MatrixSetup("elastichpc.examples.MalleableMatrixMultiplication.MatrixSetup", self)
      self.matrix_multiplication_task_port = MatrixSetup("elastichpc.examples.MalleableMatrixMultiplication.MatrixMultiplication", self)
      return

   def setServices(self, services):
      super(MatrixMultiplicationComponent, self).setServices(services)
      services.addProvidesPort(self.matrix_setup_environment_port, "MatrixSetup", "elastichpc.examples.MalleableMatrixMultiplication.MatrixSetup", None)
      services.addProvidesPort(self.matrix_multiplication_task_port, "MatrixMultiplication", "elastichpc.examples.MalleableMatrixMultiplication.MatrixMultiplication", None)
      return



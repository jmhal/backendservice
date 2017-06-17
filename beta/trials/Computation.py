import logging
import os
import time
import subprocess

def number_of_nodes():
   _file = open(os.environ['HOME'] + "/machinefile", "r")
   n = len ([ l for l in _file.readlines() if l.strip(' \n') != '' ]) 
   _file.close()
   return n

   return 
def log(msg):
   logging.debug("COMPUTATION: " + msg)
   return

def computation_unit(reconfiguration_port, computation_input):

   # wait until platform is ready.
   while (reconfiguration_port.get_actuator().value != "start"):
      time.sleep(5)
   log("Starting Computation.")

   # compute the matrix
   inputs = [ int(x) for x in computation_input.split(':') ]
   inputs_size = len(inputs)
   home = os.environ['HOME']
   for i in range(len(inputs)) :
      m = inputs[i]
      log("Matrix Size = " + str(m))
     
      nodes = 2 * number_of_nodes()
      command = ["mpirun", 
                 "-n", str(nodes), "-machinefile", home + "/machinefile", 
		 home + "/repositorios/elastichpc/beta/trials/Matrix_Work_Queue.py", 
		 str(m), "10", "0", "teste.mtr_" + str(i)]
      log(str(command))
      process = subprocess.Popen(command, stdout = subprocess.PIPE, stderr=subprocess.STDOUT)
      (output, error) = process.communicate()
      # os.remove(home + "/repositorios/elastichpc/beta/trials/" + "teste.mtr_" + str(m))
      log("Execution = " + str(output) + "|" + str(error))

      reconfiguration_port.get_sensor().value = float(i + 1) / inputs_size
      log("Progress = " + str(float(i + 1) /inputs_size))

   # finish the computation
   reconfiguration_port.get_actuator().value = "finished"
   log("Finish Computation.")

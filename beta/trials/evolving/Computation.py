import logging
import os
import time
import subprocess

def number_of_nodes():
   _file = open(os.environ['HOME'] + "/machinefile", "r")
   n = len ([ l for l in _file.readlines() if l.strip(' \n') != '' ]) 
   _file.close()
   return n

def log(msg):
   logging.debug("COMPUTATION: " + msg)
   return

def computation_unit(reconfiguration_port, computation_input):
   # wait until platform is ready.
   message = reconfiguration_port.computation_conn.recv()
   while (message[0] != "start"):
      time.sleep(5)
      message = reconfiguration_port.computation_conn.recv()
   
   log("Starting Computation.")

   # compute the matrix
   inputs = [ int(x) for x in computation_input.split(':') ]
   inputs_size = len(inputs)
   home = os.environ['HOME']

   prev_m = inputs[0]
   for i in range(len(inputs)) :
      m = inputs[i]
     
      log("Matrix Size = m : " + str(m) + "; prev_m : " + str(prev_m)) 
      if m > prev_m :
         log("Scale Up.")
         reconfiguration_port.add_node()
      elif m < prev_m :
         log("Scale Down.")
         reconfiguration_port.remove_node()
      else:
         log("Input Stable.")
      prev_m = m

      log("Start (MatrixSize, Iteration) = |" + str(m) + "|" + str(i) +"|")
      with reconfiguration_port.machine_file_lock:
         nodes = 2 * number_of_nodes()
         command = ["mpirun", 
                    "-n", str(nodes), "-machinefile", home + "/machinefile", 
	            home + "/repositorios/elastichpc/beta/trials/Matrix.py", 
		    str(m), home + "/teste.mtr_" + str(i)]
         log(str(command))
         process = subprocess.Popen(command, stdout = subprocess.PIPE, stderr=subprocess.STDOUT)
      
      (output, error) = process.communicate()
      
      log("End (MatrixSize, Iteration) = |" + str(m) + "|" + str(i) +"|")
      os.remove(home + "/teste.mtr_" + str(i))
      log("Execution = " + str(output) + "|" + str(error))
      log("Progress = " + str(float(i + 1) /inputs_size))

   # finish the computation
   reconfiguration_port.computation_conn.send(["finished"])
   log("Finish Computation.")

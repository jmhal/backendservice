#!/usr/bin/python
import os
import sys
import zmq
import numpy as np
from mpi4py import MPI
from multiprocessing import Process, Value

# Procedure executed by the control process
def control_dispatch(port, persist, progress, last_line):
   context = zmq.Context()
   socket = context.socket(zmq.REP)
   socket.bind("tcp://*:" + str(port))
   while True:
      message = socket.recv()
      #print "Control Process Message: " + message
      if message == "persist":
         persist.value = True
         socket.send(str(last_line.value))
         break;
      else:
         socket.send(str(progress.value))


# This method defines the line range for a given task, that is assigned to a worker
def get_task_range(last_line, task_size):
    return (last_line + 1, last_line + task_size)

# MPI Initialization
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

TASKFINISHEDTAG = 2
KEEPWORKINGTAG = 1
STOPWORKINGTAG = 0

# This is the dimension of the square matrices.
N = int(sys.argv[1])

# This is the task size. It's the number of lines each worker will compute from C.
# N must be divisible by task_size and size, and task_size must be great than size.
task_size = int(sys.argv[2])

# Send B to everyone
# Suppose B is read from a file. This can be done in rank 0 and later broadcasted for everyone.
# Right now, doesn't make any sense. 
B = np.ones((N,N), dtype=float)
comm.Bcast(B, root = 0)

if rank == 0:
   # MPI variable for status of communication directives
   status = MPI.Status()
   
   # The progress variable holds the percentage of work done.
   # The persist variable informs the rank 0 process if it should save the work and quit.
   # The last_line variable holds the last line from C computed. After persisting the computation, the control
   # process returns this value to the root unit of the Computation Component.
   # The control process deals with the exchange of these values with the root unit of the Computation component.
   progress = Value('i', 0, lock = True)
   persist = Value('b', False, lock = True)
   last_line = Value('i', -1, lock = True)
   last_line.value = int(sys.argv[3])
   control_process = Process(target = control_dispatch, args=(33002, persist, progress, last_line))
   # #print "Starting Control Process."
   control_process.daemon = True
   control_process.start()

   # The Matrices A and C
   A = np.ones((N,N), dtype=float)  
   C = np.zeros((N,N), dtype=float)

   # Verify if the matrix file exists.
   file_name = sys.argv[4]
   if os.path.isfile(file_name):
      #print "Reading Matrix from File."
      C = np.loadtxt(file_name)
      #print "Restarting Computation from Line: %d" % last_line.value
   else:
      # Otherwise, compute from the beginning.
      # The value passed as a parameter is just ignored.
      #print "Starting Computation."
      last_line.value = -1 
      

   # Dictionary with the last assignments
   # For each process rank used as a key, it returns a tuple with the last
   # range of columns of C assigned to this process
   work_assignment = {}

   # Loop over all the workers, sending one task each  
   # We exclude rank 0, but worker 1 receives the task 0, worker 2 the task 1, and so on...
   for worker in range(1, size):
      task_range = get_task_range(last_line.value, task_size)
      work_assignment[worker] = task_range
      last_line.value = task_range[1]
      sendbuffer = A[task_range[0]:(task_range[1] + 1)]
      # #print "task range 0: %d task range 1: %d task size: %d" % (task_range[0], task_range[1], task_size)
      comm.Send(sendbuffer.reshape(task_size * N), dest = worker, tag = KEEPWORKINGTAG)
      # #print "sending range %d %d to worker %d" % (task_range[0], task_range[1], worker)

   # Start receiving the work done and sends new tasks
   remaining_tasks = (N - last_line.value) / task_size
   remaining_results = remaining_tasks + size - 1
   #print "Remaining_tasks: %d, Remaining_results: %d" % (remaining_tasks, remaining_results)

   # This is the main loop.
   while (remaining_tasks != 0) or (remaining_results != 0):
      # Receive a slice of C
      if remaining_results != 0:
         recvbuffer = np.zeros(task_size * N, dtype = float)
         comm.Recv(recvbuffer, source = MPI.ANY_SOURCE, tag = TASKFINISHEDTAG, status = status)
      
         # Find out where to place the slice of C in the final C matrix
         source = status.Get_source()
         C_range = work_assignment[source]
         C[C_range[0]:(C_range[1]+1)] = recvbuffer.reshape(task_size, N)
         remaining_results = remaining_results - 1

         # #print "receiving range %d %d from worker %d" % (C_range[0], C_range[1], source)

      # Progress is defined by the last line calculated.
      progress.value = last_line.value + 1
      #print "Setting Progress to: %d / %d = %.2f, remaining_tasks = %d, remaining_results = %d" % (last_line.value, N, progress.value, remaining_tasks, remaining_results)

      # Send new work
      if remaining_tasks != 0:
         task_range = get_task_range(last_line.value, task_size)
         sendbuffer = sendbuffer = A[task_range[0]:(task_range[1] + 1)]
         work_assignment[source] = task_range
         last_line.value = task_range[1]
         comm.Send(sendbuffer.reshape(task_size * N), dest = source, tag = KEEPWORKINGTAG)
	 remaining_tasks = remaining_tasks - 1

         # #print "sending new work with range %d %d for worker %d" % (task_range[0], task_range[1], source)
 
      # Stop sending new tasks if you should save the work
      if (persist.value == True):
         # #print "The Computation Will Persist. Remaining_Results %d" % remaining_results
         remaining_tasks = 0 
         if remaining_results > size:
            remaining_results = size - 1
     
      # #print "remaining tasks %d remaining results %d" % (len(remaining_tasks), remaining_results)

   # Say bye bye to the workers
   for worker in range(1, size):
      #print "Stopping Worker %d" % worker
      sendbuffer = np.zeros(1)
      comm.Send(sendbuffer, dest = worker, tag = STOPWORKINGTAG)
   
   # #print C

   # Save matrix to file
   #print "Saving Matrix to File."
   np.savetxt(file_name, C)
   #print "Matrix Saved to File."

   # Finish the control process
   control_process.terminate()   

else:
   # The worker code remains unchanged for the reconfigurable version.
   # A worker process receives a slice of A, and since it already has B,
   # a slice of C is computed. The process does not need to know where the
   # slice of A fits in the full matrix A. 
   status = MPI.Status()
   while (True):
      # Recover a slice of A
      recvbuffer = np.zeros((task_size, N), dtype = float)
      comm.Recv(recvbuffer.reshape(task_size * N), source = 0, tag = MPI.ANY_TAG, status = status)
      if status.Get_tag() == STOPWORKINGTAG :
         #print "Worker %d Stopping." % rank
         break
 
      # Do the work
      A_worker = recvbuffer.reshape(task_size, N)
      C_worker = np.zeros((task_size, N), dtype = float)
      np.matmul(A_worker, B, C_worker)

      # Send back a slice of C
      sendbuffer = C_worker.reshape(task_size * N)
      comm.Send(sendbuffer, dest = 0, tag = TASKFINISHEDTAG)



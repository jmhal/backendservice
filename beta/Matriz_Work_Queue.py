#!/usr/bin/python
import sys
import numpy as np
from mpi4py import MPI

# Auxiliary methods
def get_task_range(A, N, task_size, task_number):
#   return (task_number * N / task_size, (task_number + 1) * N / task_size)
    return (task_number * task_size, (task_number + 1) * task_size)

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
# Suppose B is read from a file. This can be done in rank 0 and later broadcast for everyone.
# Right now, doesn't make any sense. 
B = np.ones((N,N), dtype=float)
comm.Bcast(B, root = 0)

if rank == 0:
   status = MPI.Status()
   
   # The Matrices A and C
   A = np.ones((N,N), dtype=float)  
   C = np.zeros((N,N), dtype=float)

   # Dictionnary with the last assignments
   work_assignment = {}

   # Loop over all the workers, sending one task each  
   # We exclude rank 0, but worker 1 receives the task 0, worker 2 the task 1, and so on...
   for worker in range(1, size):
      task_range = get_task_range(A, N, task_size, worker - 1)
      work_assignment[worker] = task_range
      sendbuffer = A[task_range[0]:task_range[1]]
      # print "task range 0: %d task range 1: %d task size: %d" % (task_range[0], task_range[1], task_size)
      comm.Send(sendbuffer.reshape(task_size * N), dest = worker, tag = KEEPWORKINGTAG)
      # print "sending range %d %d to worker %d" % (task_range[0], task_range[1], worker)

   # Start receiving the work done and sending again
   remaining_tasks = range(size - 1, N / task_size)
   remaining_results = range(N / task_size)
   while (len(remaining_tasks)!= 0) or (len(remaining_results) != 0):
      # Receive a slice of C
      if len(remaining_results) != 0:
         recvbuffer = np.zeros(task_size * N, dtype = float)
         comm.Recv(recvbuffer, source = MPI.ANY_SOURCE, tag = TASKFINISHEDTAG, status = status)
      
         # Find out where to place the slice of C in the final C matrix
         source = status.Get_source()
         C_range = work_assignment[source]
         C[C_range[0]:C_range[1]] = recvbuffer.reshape(task_size, N)
         remaining_results = remaining_results[1:]  

         # print "receiving range %d %d from worker %d" % (C_range[0], C_range[1], source)

      # Send new work
      if len(remaining_tasks) != 0:
         task = remaining_tasks[0] 
	 remaining_tasks = remaining_tasks[1:]
         task_range = get_task_range(A, N, task_size, task)
         sendbuffer = sendbuffer = A[task_range[0]:task_range[1]]
         work_assignment[source] = task_range
         comm.Send(sendbuffer.reshape(task_size * N), dest = source, tag = KEEPWORKINGTAG)

         # print "sending new work with range %d %d for worker %d" % (task_range[0], task_range[1], source)
      
      # print "remaining tasks %d remaining results %d" % (len(remaining_tasks), len(remaining_results))

   # Say bye bye to the workers
   for worker in range(1, size):
      sendbuffer = np.zeros(1)
      comm.Send(sendbuffer, dest = worker, tag = STOPWORKINGTAG)
   
   # print C
      
else:
   status = MPI.Status()
   while (True):
      # Recover a slice of A
      recvbuffer = np.zeros((task_size, N), dtype = float)
      comm.Recv(recvbuffer.reshape(task_size * N), source = 0, tag = MPI.ANY_TAG, status = status)
      if status.Get_tag() == STOPWORKINGTAG :
         break
 
      # Do the work
      A_worker = recvbuffer.reshape(task_size, N)
      C_worker = np.zeros((task_size, N), dtype = float)
      np.matmul(A_worker, B, C_worker)

      # Send back a slice of C
      sendbuffer = C_worker.reshape(task_size * N)
      comm.Send(sendbuffer, dest = 0, tag = TASKFINISHEDTAG)



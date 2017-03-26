#!/usr/bin/python

import sys
import numpy as np
from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

N = int(sys.argv[1])

A = None
C = None
if rank == 0:
   A = np.ones((N,N), dtype=float)  
   C = np.zeros((N,N), dtype=float)

A_worker = np.zeros((N/size,N), dtype=float)  
C_worker = np.zeros((N/size,N), dtype=float)
  
# Everyone needs a full copy of B
B = np.ones((N,N), dtype=float)

# Scatter A
sendbuffer = None
if rank == 0:
   sendbuffer = A.reshape([size, N * N / size])
comm.Scatter(sendbuffer, A_worker.reshape(N * N / size), root=0)

# Broadcast B
comm.Bcast(B, root = 0)

# Do the work
#for i in range(N / size):
#   for j in range(N):
#      for k in range(N):
#         C_worker[i][j] += A_worker[i][k] * B[k][j]
np.matmul(A_worker, B, C_worker)

# Gather C
recvbuffer = None
if rank == 0:
   recvbuffer = C.reshape(N * N)
comm.Gather(C_worker.reshape(N * N / size), recvbuffer, root = 0)

if ((N <= 20) and (rank == 0)): 
   print C

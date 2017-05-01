#!/usr/bin/python
import sys
import numpy as np

if __name__ == "__main__":
   N = int(sys.argv[1])
   file_name = sys.argv[2]
   M = np.ones((N,N), dtype=float)
   np.save(file_name, M)



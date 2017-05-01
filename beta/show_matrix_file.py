#!/usr/bin/python
import sys
import numpy as np

if __name__ == "__main__":
   file_name = sys.argv[1]
   M = np.load(file_name)
   print M



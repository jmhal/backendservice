#!/usr/bin/python
import re
import sys

_file = sys.argv[1]

progress_status = []
cost = 0
prev_time = 0
# From the contract
prev_nodes = 2

with open(_file) as origin_file:
   for line in origin_file:
      if "State" in line:
         data = line.split('=')[1]
         time = float(data.split(';')[0].split(':')[1])
         progress = float(data.split(';')[1].split(':')[1])
         progress = round(progress * 20)
         if progress in progress_status:
            continue
         else: 
            progress_status.append(progress)
         efficiency = float(data.split(';')[2].split(':')[1].split('|')[0])
         nodes = float(data.split(';')[3].split(':')[1])

         cost += (time - prev_time) * prev_nodes
         prev_time = time
         prev_nodes = nodes
         print progress, time, efficiency, nodes, cost

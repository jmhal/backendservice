#!/usr/bin/python
from tabulate import tabulate

data = []

for vms in [2, 6, 8]:
   for matrix_size in [1000, 2000, 3000, 4000, 5000, 6000, 7000, 8000, 9000, 10000]:
      filename = "computational_system_" + str(vms) + "_20_" + str(matrix_size) + ".log"
      with open(filename, "r") as _log:
         for line in _log:
            if "Execution Log" in line:
               log_list = eval(line.split('=')[1].strip())

               start_time = log_list[0][0]
               end_time = log_list[-1][0]
               elapsed = end_time - start_time
               
               cpu_load = 0.0
               memory_load = 0.0
               for event in log_list:
                  cpu_load += float(event[1]['resource_state'].split('|')[0])
                  memory_load += float(event[1]['resource_state'].split('|')[1])
               cpu_load /= len(log_list)
               memory_load /= len(log_list)

               cost = 0.0
               previous_vms = None
               previous_time = None
               for event in log_list:
                  if (previous_time == None) and (previous_vms == None):
                     previous_time = event[0]
                     previous_vms = event[1]['nodes']
                  else:
                     cost += (event[0] - previous_time) * previous_vms
                     previous_time = event[0]
                     previous_vms = event[1]['nodes']

               data.append([vms, matrix_size, elapsed, cpu_load, memory_load, cost])
            
print tabulate(data, headers=["VMS", "Matrix_Size", "Elapsed", "Average CPU Load", "Average Memory Load", "Cost"], floatfmt=".2f")

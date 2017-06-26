 nl computational_system_static_6_5000_interference.log | grep mpirun | awk '{print $1}' | while read line; do sed -n $line,$(($line+1))p computational_system_static_6_5000_interference.log >> filtered.log ; done;
 awk -F'|' '{print NR,($1 - 1498476660.667612),$4}'  filtered_6_5000_interference.log

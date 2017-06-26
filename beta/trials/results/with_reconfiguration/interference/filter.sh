#!/bin/bash
log_file=$1
export start_time=$2
 
nl $log_file | grep mpirun | awk '{print $1}' | while read line; do sed -n $line,$(($line+1))p $log_file >> f1.temp ; done;
grep PLATFORM f1.temp > f2.temp
awk -F'|' '{print NR,($1 - ENVIRON["start_time"]),$4}' f2.temp > f3.temp

rm f1.temp f2.temp
mv f3.temp output.plot

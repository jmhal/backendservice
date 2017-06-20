#!/bin/bash

for cluster_size in 2 6 8
do
   for N in 1000 2000 3000 4000 5000 6000 7000 8000 9000 10000
   do
      ./run_system.sh $cluster_size 20 $N
   done
done

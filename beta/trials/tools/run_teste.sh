#!/bin/bash
file="temp.mtr"

for size in 1000 2000 3000 4000 5000 6000 7000 8000 9000 10000
do
   for p in 2 4 6 8 10 12 14 16 18 20
   do
      echo "Running matrix size $size for $p processes..."
      start=`date +%s`
      mpirun --machinefile $HOME/machinefile -np $p $HOME/repositorios/elastichpc/beta/trials/Matrix_Work_Queue.py $size 10 0 $file$p
      end=`date +%s`
      elapsed=$(expr $end - $start)
      echo "Elapsed Time for matriz size $size with $p processes: $elapsed"
      rm $file$p
   done
done

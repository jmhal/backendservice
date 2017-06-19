#!/bin/bash

for r in 1 2 3 4 5 6 7 8 9 10 11 12 
do
   echo "Rodada $r"
   ./reconfiguration_time.py rodada$r.log; 
   sleep 60;
done

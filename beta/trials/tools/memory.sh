#!/bin/bash

# process machinefile
machine_file() {
   file="$HOME/machinefile"
   list=`awk -F: 'BEGIN{v=""} {(NR == 1) ? v=$1 : v=v","$1} END {print v}' $file`
   echo $list
}

list=`machine_file`

memory=$(pdsh -R ssh -w $list free -m 2> /dev/null | grep Mem | awk 'BEGIN{ mem=0 }{mem = mem + $4}END{print mem/NR}')
cpu=$(pdsh -R ssh -w $list cat /proc/loadavg | awk 'BEGIN { cpu=0.0 } {cpu = cpu + $2} END { if (cpu == 0) {print cpu;} else {print cpu/NR;}}')

if [ $# -gt 0 ]
then

   if [ $1 == "cpu" ] 
   then
      echo $cpu;
   elif [ $1 == "memory" ] 
   then
      echo $memory;
   fi
else
   echo $cpu:$memory 
fi

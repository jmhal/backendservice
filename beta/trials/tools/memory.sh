#!/bin/bash

# process machinefile
machine_file() {
   file="$HOME/machinefile"
   list=`awk -F: 'BEGIN{v=""} {(NR == 1) ? v=$1 : v=v","$1} END {print v}' $file`
   echo $list
}

list=`machine_file`

memory=$(pdsh -R ssh -w $list free -m 2> /dev/null | grep Mem | awk 'BEGIN{ mem=0 }{mem = mem + $5}END{print mem/NR}')

echo $memory

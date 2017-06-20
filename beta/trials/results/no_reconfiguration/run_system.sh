#!/bin/bash

# simulation parameters 
cluster_size=$1
runs=$2
N=$3
qos_values="0:0:0:0:0"
qos_weights="0:0:0:0:0"
qos_factor="0.0"
qos_intervals="10:10:10"

# create computational input
separator=":"
computational_input=""
for i in `seq $runs`
do
   if [ $i -eq 1 ]
   then
      computational_input=$N
   else
      computational_input=$computational_input$separator$N
   fi
done
echo $computational_input

# run the system
profile_file="/home/joaoalencar/repositorios/elastichpc/beta/trials/results/no_reconfiguration/profiles/profile_${cluster_size}.yaml"
echo "Running with parameters = static $profile_file $qos_values $qos_weights $qos_factor $qos_intervals $computational_input"
python ~/repositorios/elastichpc/beta/trials/infrastructure/backendservice.py static ~/openstack/keystonerc_joaoalencar $profile_file $qos_values $qos_weights $qos_factor $qos_intervals $computational_input 

# renaming log
if [ -f "computational_system.log" ]
then
   mv computational_system.log computational_system_${cluster_size}_${runs}_${N}.log
else
   echo "computational_system.log not found."
fi

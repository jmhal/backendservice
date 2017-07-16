#!/bin/bash
source ~/openstack/keystonerc_admin
for instance in $(nova list --all | grep "head_node\|compute_node" | cut -f2 -d'|')
do 
   nova show $instance | grep hypervisor | cut -d '|' -f3
done;

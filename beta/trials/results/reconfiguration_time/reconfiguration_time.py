#!/usr/bin/python
import sys
from datetime import datetime
from infrastructure.cloud import OpenStack
from infrastructure.common import parse_profile

_file = open(sys.argv[1], "w")

profile = parse_profile("/home/joaoalencar/repositorios/elastichpc/beta/trials/infrastructure/profile.yaml")
openstack = OpenStack("/home/joaoalencar/openstack/keystonerc_joaoalencar")

start = int(datetime.now().strftime('%s'))
stack_id = openstack.deploy_profile("teste", profile['template_file'], profile['params'])
end = int(datetime.now().strftime('%s'))

_file.write("creation|" + str(end - start) + "|\n")

for size in range(1, 10):
   profile['params']['cluster_size'] = size

   start = int(datetime.now().strftime('%s'))
   openstack.update_profile("teste", stack_id, profile['template_file'], profile['params'])
   end = int(datetime.now().strftime('%s'))

   ip = openstack.get_ips("teste", stack_id)['floating_ip']

   _file.write("scaleout" + "|" + str(size) + "|" + str(end - start) + "|" + ip + "\n")

for size in range(9,0,-1):
   profile['params']['cluster_size'] = size

   start = int(datetime.now().strftime('%s'))
   openstack.update_profile("teste", stack_id, profile['template_file'], profile['params'])
   end = int(datetime.now().strftime('%s'))

   ip = openstack.get_ips("teste", stack_id)['floating_ip']

   _file.write("scale" + "|" + str(size) + "|" + str(end - start) + "|" + ip + "\n")

openstack.destroy_profile("teste", stack_id)

_file.close()

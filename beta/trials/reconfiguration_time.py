import sys
from datetime import datetime
from infrastructure.cloud import OpenStack
from infrastructure.common import parse_profile

_file = open(sys.argv[1], "w")

profile = parse_profile("infrastructure/profile.yaml")
openstack = OpenStack("/home/joaoalencar/openstack/keystonerc_joaoalencar")

start = datetime.now()
stack_id = openstack.deploy_profile("teste", profile['template_file'], profile['params'])
end = datetime.now()

_file.write("creation:" + str(end - start) + "\n")

for size in range(2, 10):
   profile['params']['cluster_size'] = size

   start = datetime.now()
   openstack.update_profile("teste", stack_id, profile['template_file'], profile['params'])
   end = datetime.now()

   ip = openstack.get_ips("teste", stack_id)['floating_ip']

   _file.write("expand" + str(size) + ":" + str(end - start) + ":" + ip + "\n")

for size in range(8,0,-1):
   profile['params']['cluster_size'] = size

   start = datetime.now()
   openstack.update_profile("teste", stack_id, profile['template_file'], profile['params'])
   end = datetime.now()

   ip = openstack.get_ips("teste", stack_id)['floating_ip']

   _file.write("shrink" + str(size) + ":" + str(end - start) + ":" + ip + "\n")


openstack.destroy_profile("teste", stack_id)

_file.close()

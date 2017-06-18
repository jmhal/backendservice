import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

from infrastructure.cloud import OpenStack
from infrastructure.common import parse_profile

profile_dict = None
openstack = None

def changeNodeNumber(stack_name, stack_id, n = 0):
   global profile_dict
   global openstack
   new_node_count = profile_dict['params']['cluster_size'] + 1 + n
     
   if new_node_count > profile_dict['nodes'][2] or new_node_count < profile_dict['nodes'][0]:
      return "OUTOFRANGE" 
	  
   profile_dict['params']["cluster_size"] = new_node_count - 1
        
   status = openstack.update_profile(stack_name, stack_id, profile_dict['template_file'], profile_dict['params'])
      
   if status != 202:
      return "FAILED"
   return "BUILDING"

def add_node(stack_name, stack_id, n = 1):
   return changeNodeNumber(stack_name, stack_id, n)

def remove_node(stack_name, stack_id, n = 1):
   return changeNodeNumber(stack_name, stack_id, -n)

def get_ips(stack_name, stack_id):
   global openstack
   # return openstack.get_ips(stack_name, stack_id)
   # a bug sometimes stops head_node_ip from being retrieved
   d = openstack.get_ips(stack_name, stack_id)
   if d['head_node_ip'] == None:
      d['head_node_ip'] = "10.10.10.3"
   return d

def start_server(credentials, profile, address, port):
   global profile_dict
   global openstack
   
   # Create OpenStack
   openstack = OpenStack(credentials)
   profile_dict = parse_profile(profile)

   # Register Elasticity Methods
   server = SimpleXMLRPCServer((address, port))
   server.register_function(add_node, "add_node")
   server.register_function(remove_node, "remove_node")
   server.register_function(get_ips, "get_ips")

   # Run Server
   server.serve_forever()

if __name__ == '__main__':
   start_server("/home/joaoalencar/openstack/keystonerc_joaoalencar", "/home/joaoalencar/repositorios/elastichpc/beta/trials/infrastructure/profile.yaml", "200.19.177.89", 33004)



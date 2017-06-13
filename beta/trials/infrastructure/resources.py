import yaml
import paramiko
from infrastructure.cloud import OpenStack
from infrastructure.common import parse_profile
from infrastructure.common.ssh import SSH

class Resources():
   def __init__(self, stack_name, stack_id):
      # openstack services
      self.openstack = OpenStack("/home/ubuntu/credentials")

      # profile information
      self.profile_dict = parse_profile("/home/ubuntu/profile")
      self.min_node = self.profile_dict['nodes'][0]
      self.node_count = self.profile_dict['nodes'][1] + 1
      self.max_node = self.profile_dict['nodes'][2]
   
      # stack name and stack id
      self.stack_id = stack_id
      self.stack_name = stack_name
     
      # ssh setup
      self.ssh = SSH("ubuntu", "/home/ubuntu/.ssh/id_rsa.pub", 22)

   def configure_machine_file(self):
      machinefile = open("/home/ubuntu/machinefile", "w")
      
      ips = self.openstack.get_ips(self.stack_name, self.stack_id)
      
      machinefile.write(ips['head_node_ip'] + ":" + str(self.cores))
      for machine in ips['compute_node_ips']:
         machinefile.write(machine + ":" + str(self.cores))
      machinefile.close()
      
      return 

   def addNode(self, n = 1):
      return self.changeNodeNumber(n)
       
   def removeNode(self, n = 1):
      return self.changeNodeNumber(-n)

   def changeNodeNumber(self, n = 0):
      new_node_count = self.node_count + n
     
      if new_node_count > self.max_node or new_node_count < self.min_node:
	   return None
	  
      self.profile_dict['params']["cluster_size"] = new_node_count - 1
        
      status = self.openstack.update_profile(self.stack_name, self.stack_id, self.profile_dict['template_file'], self.profile_dict['params'])
      
      if status != 202:
         return "FAILED"
      else:
         self.number_of_nodes = new_node_count 
         return "BUILDING"

   def getResourceState(self):
      pass 

import os
import sys
import uuid

from multiprocessing import Process
from infrastructure.cloud import OpenStack
from infrastructure.common import parse_profile
from infrastructure.common.ssh import SSH
from infrastructure.resources.server import start_server

class BackEndService:
   def __init__(self, credentials):
      self.credentials = credentials
      self.openstack = OpenStack(credentials)
      
      # ssh configuration
      self.ssh = SSH("ubuntu", self.openstack.parse_rc(credentials)["OS_KEYFILE"], 22)

   def deploy_platform(self, profile):
      self.stack_name = "elastic_cluster_" + str(uuid.uuid4())
      profile_dict = parse_profile(profile)
      
      self.stack_id = self.openstack.deploy_profile(stack_name, profile_dict['template_file'], profile_dict['params'])

      return (self.stack_name, self.stack_id)

   def destroy_platform(self, stack_name, stack_id):
      return self.openstack.destroy_profile(stack_name, stack_id)

   def go(self, profile, qos_values, qos_weights, qos_factor, qos_intervals, computation_input):
      # deploy platform
      (stack_name, stack_id) = self.deploy_platform(profile)
      print "Stack Name: " + str (stack_name)
      print "Stack ID: " + str(stack_id)

      # start ResourceServer
      # (credentials, profile, stack_name, stack_id)
      url = "http://" + "200.19.177.89" + ":" + "33004"
      server = Process(target = start_server, args=(self.credentials, profile, "200.19.177.89", 33004))
      server.daemon = True
      server.start()
      
      # execute the Computational System remotely  
      floating_ip = self.openstack.get_ips(stack_name, stack_id)['floating_ip']
      cmd = "repositorios/elastichpc/beta/trials/System.py " +url + " " + stack_name + " " + stack_id + " " + qos_values + " " + qos_weights + " " + qos_factor + " " + qos_intervals+ " " + computation_input 
      output = self.ssh.run_command(floating_ip, cmd)

      # destroy the platform
      # server.terminate()
      # self.destroy_platform(stack_name, stack_id)
     
      return output
   
if __name__ == '__main__':
   credentials_file = sys.argv[1]   
   profile_file = sys.argv[2]       
   qos_values = sys.argv[3]             # a:t:e:c:p
   qos_weights = sys.argv[4]            # wa:wt:we:wc:wp
   qos_factor = sys.argv[5]             # alfa
   qos_intervals = sys.argv[6]          # monitoring:sample:reconfiguration
   computation_input = sys.argv[7]

   service = BackEndService(credentials_file)
   print "SAIDA: " +  service.go(profile_file, qos_values, qos_weights, qos_factor, qos_intervals, computation_input)
   



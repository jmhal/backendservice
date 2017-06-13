import yaml
import sys
import uuid
import paramiko
from cloud import OpenStack

class BackEndService:
   def __init__(self, credentials):
      self.openstack = OpenStack(credentials)
      
      # ssh configuration
      self.username = "ubuntu"
      self.keyfile = self.openstack.parse_rc(credentials)["OS_KEYFILE"]
      self.port = 22
      self.ssh = paramiko.SSHClient()

   def parse_profile(self, profile):
      output = {}
      # profile
      profile_file = open(profile, "r")
      profile_dict = yaml.load(profile_file)
     
      template_dir = profile_dict["profile"]["template_dir"]
      template = profile_dict["profile"]["template"]
      template_file = template_dir + "/" + template
      output['template_file'] = template_file

      number_of_nodes = profile_dict["profile"]["parameters"]["cluster_size"] + 1
      min_node = profile_dict["profile"]["nodes"]["min"]
      max_node = profile_dict["profile"]["nodes"]["max"]
      output['nodes'] = (min_node, number_of_nodes, max_node)

      params = profile_dict["profile"]["parameters"]
      output['params'] = params

      profile_file.close()

      return output

   def run_command(self, ip, cmd):
      self.connect(ip)
      ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(cmd)
      output = ""
      for line in ssh_stdout.readlines():
           output = output + line
      self.disconnect()
      return output

   def connect(self, ip):
      self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      self.ssh.connect(ip, self.port, username=self.username, key_filename=self.keyfile)

   def disconnect(self):
      self.ssh.close()
 
   def deploy_platform(self, profile):
      stack_name = "elastic_cluster_" + str(uuid.uuid4())
      profile_dict = self.parse_profile(profile)
      
      stack_id = self.openstack.deploy_profile(stack_name, profile_dict['template_file'], profile_dict['params'])

      return (stack_name, stack_id)

   def destroy_platform(self, stack_name, stack_id):
      return self.openstack.destroy_profile(stack_name, stack_id)

   def go(self, profile, computation_input):
      # deploy platform
      (stack_name, stack_id) = self.deploy_platform(profile)

      # recover head_node_ip
      head_node_ip = self.openstack.get_ips(stack_name, stack_id)['floating_ip']

      # execute the Computational System remotely  
      min_node = self.parse_profile(profile)['nodes'][0]
      number_of_nodes = self.parse_profile(profile)['nodes'][1]
      max_node = self.parse_profile(profile)['nodes'][2]
      cmd = "/home/ubuntu/repositorios/elastichpc/beta/trials/System.py " + stack_name + " " + stack_id + " " + str(min_node) + " " + str(number_of_nodes) + " " + str(max_node) + " " + computation_input 
      output = self.run_command(head_node_ip, cmd)

      # destroy the platform
      self.destroy_platform(stack_name, stack_id)

      return output
   
if __name__ == '__main__':
   credentials_file = sys.argv[1]   
   profile_file = sys.argv[2]       
   computation_input = sys.argv[3]

   service = BackEndService(credentials_file)
   print "SAIDA: " +  service.go(profile_file, computation_input)
   



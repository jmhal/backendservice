import json
import requests
import os
import yaml
import time
import logging
import uuid
import sys
import paramiko

from os import environ as env
from os import path as path
from datetime import datetime
from heatclient.common import template_utils

class Resources:
    def __init__(self, credentials, ips, cores):
       self.cores = cores
       self.ips = ips
       self.credentials = credentials

       self.username = "ubuntu"
       self.port = 22
       self.ssh = paramiko.SSHClient()

    def runCommand(self, cmd):
       self.connect()
       ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(cmd)
       output = ""
       for line in ssh_stdout.readlines():
            output = output + line
       self.disconnect()
       return output

    def connect(self):
       self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
       self.ssh.connect(self.ips['floating_ip'], self.port, username=self.username, key_filename=self.credentials)

    def disconnect(self):
       self.ssh.close()
 
    def getMachineFile(self):
       machinefile = self.ips['head_node_ip'] + ":" + str(self.cores) + "\n"
       self.runCommand("echo " + self.ips['head_node_ip'] + ":" + str(self.cores) + " > machinefile")
       for machine in self.ips['compute_node_ips']:
          machinefile += machine + ":" + str(self.cores) + "\n"
	  self.runCommand("echo " + machine + ":" + str(self.cores) + " >> machinefile")
       return machinefile  

class OpenStackCloud:
    def __init__(self, credentials, profile):
        # Unique ID for this cluster
	self.deployment_id = uuid.uuid4()

        # credentials
	_dict = self.parse_rc(credentials)
        self.username = _dict["OS_USERNAME"]
	self.password = _dict["OS_PASSWORD"]
	self.key_file = _dict["OS_KEYFILE"]
	self.auth_url = _dict["OS_AUTH_URL"]
        self.heat_base_url = "http://" + self.auth_url.split(":")[1][2:] + ":8004/v1"
	self.tenant_name = _dict["OS_TENANT_NAME"]
	self.region_name = _dict["OS_REGION_NAME"]

	# profile
	profile_file = open(profile, "r")
	profile_dict = yaml.load(profile_file)
	self.template_dir = profile_dict["profile"]["template_dir"]
        self.template = profile_dict["profile"]["template"]
        self.template_file = self.template_dir + "/" + self.template
	self.number_of_nodes = profile_dict["profile"]["parameters"]["cluster_size"] + 1
	self.min_node = profile_dict["profile"]["nodes"]["min"]
	self.max_node = profile_dict["profile"]["nodes"]["max"]
	self.params = profile_dict["profile"]["parameters"]
	profile_file.close()

	# token
        self.token_create_time = datetime.now()
        self.token = self.get_auth_token(self.auth_url + "/tokens", self.tenant_name, self.username, self.password)

        # name of the stack and the tenant id
        self.stack_name = profile_dict["profile"]["name"] + str(self.deployment_id)
        self.tenant_id = self.get_tenant_id(self.auth_url + "/tenants", self.token, self.tenant_name)

        # cluster resources
	self.resources = None

        # status messages
        self.results_status = {
           'CREATE_IN_PROGRESS': "BUILDING",
           'CREATE_COMPLETE':"READY",
           'DELETE_IN_PROGRESS': "DESTROYED",
           'DELETE_COMPLETE': "DESTROYED",
           'CREATE_FAILED': "FAILED",
	   'UPDATE_IN_PROGRESS': "BUILDING",
	   'UPDATE_COMPLETE': "READY"
        }
       
	# configure logging
	logging.basicConfig(level=logging.DEBUG)
	self.logger = logging.getLogger(__name__)

    def getResources(self):
       """
       Returns the nodes, as a machine file for MPI
       node0:corecount
       node1:corecount
       node2:corecount
       ...
       """
       self.resources = Resources(self.key_file, self.get_ips(), 2)
       self
       return self.resources

    def getClusterStatistics(self):
       """
       Returns the overall status of the cluster. 
       For the CPU, Memory, Disk and Bandwidth, is the average for the values of each node.
       For the cost, is the sum of the value of each node. 
       sample output: {"cpuload": 0.5, "memory" : 0.5, "diskusage": 0.5, "network" : 0.5, "cost" : 13.4 }
       """
       if self.resources == None:
          return None
       else :
          raise NotImplementedError("Abstract Class!")
 
    def addNode(self, n = 1):
       return self.changeNodeNumber(n)
       
    def removeNode(self, n = 1):
        return self.changeNodeNumber(-n)
	
    def parse_rc(self, rc_filename):
       """
       Parse OpenStack credentials file to dict.
       """
       _file = open(rc_filename, "r")
       _dict = {}
       for line in _file.readlines():
          try:
             key = line.split(" ")[1].split('=')[0].rstrip()
             value = line.split(" ")[1].split('=')[1].rstrip()
             _dict[key] = value
          except IndexError as e:
	     # skip any blank lines
             continue
       _file.close()
       return _dict 

    def authenticate(self):
        """
        Create a token for the heat API calls.
        """
        now = datetime.now()
        difference = now - self.token_create_time
        if difference.seconds > 60 * 60:
           self.token = self.get_auth_token(self.auth_url + "/tokens", self.tenant_name, self.username, self.password)
        return self.token

    def allocate_resources(self):
        """
        Deploy the template stack.
        """
        self.authenticate()
        
        self.stack_id = self.create_stack(token = self.token, tenant_id = self.tenant_id, heat_base_url = self.heat_base_url,
                        stack_name = self.stack_name, template_file = self.template_file, params = self.params)

        while self.allocation_status() == "BUILDING" :
	   time.sleep(10)
       
        return self.stack_id

    def allocation_status(self):
        """
        How is the stack? 
        """
        self.authenticate()

        status = self.status_stack(token = self.token, tenant_id = self.tenant_id, heat_base_url = self.heat_base_url,
                     stack_name = self.stack_name, stack_id = self.stack_id)
        
	heat_status = status['stack']['stack_status']
        return self.results_status[heat_status]

    def get_ips(self):
        self.authenticate()

        while self.allocation_status() == "BUILDING" :
	   time.sleep(10)

        status = self.status_stack(token = self.token, tenant_id = self.tenant_id, heat_base_url = self.heat_base_url,
                     stack_name = self.stack_name, stack_id = self.stack_id)
        outputs = status['stack']['outputs']
	ips = {}
	for d in outputs:
           ips[d['output_key']] = d['output_value']
	return ips

    def deallocate_resources(self):
        """
        Destroy the stack.
        """
        self.authenticate()

        self.delete_stack(token = self.token, tenant_id = self.tenant_id , heat_base_url = self.heat_base_url ,
                          stack_name = self.stack_name, stack_id = self.stack_id)

        return "DESTROYED" 

    def changeNodeNumber(self, n = 0):
        self.authenticate()

        while self.allocation_status() == "BUILDING" :
	   time.sleep(10)

        if self.allocation_status() != "READY" :
	   return None
	
	new_node_count = self.number_of_nodes + n
        if new_node_count > self.max_node or new_node_count < self.min_node:
	   return None
	  
	self.params["cluster_size"] = new_node_count - 1
        
	status = self.update_stack(token = self.token, tenant_id = self.tenant_id, heat_base_url = self.heat_base_url, 
	                           stack_name = self.stack_name, stack_id = self.stack_id, template_file = self.template_file, params = self.params)

        if status != 202:
	   return "FAILED"
	else:
	   self.number_of_nodes = new_node_count 
           return "BUILDING"

    def get_auth_token(self, url, tenant_name, username, password):
        headers = {'Content-Type':'application/json'}
        fields = {
            'auth':{
                'tenantName': tenant_name,
                'passwordCredentials':{
                    'username': username,
                    'password': password}
                 }
        }
        r = requests.post(url, data = json.dumps(fields), headers = headers)
        token_id = r.json()['access']['token']['id']
        return token_id

    def get_tenant_id(self, url, token, tenant):
       headers = {'X-Auth-Token': token}
       r = requests.get(url, headers=headers)
       json = r.json()
       for element in json['tenants']:
          if element['name'] == tenant:
              return element['id']
       return None

    def create_stack(self, token, tenant_id, heat_base_url, stack_name, template_file, params):
        headers = {'X-Auth-Token': token}
        tpl_files, template = template_utils.get_template_contents(template_file = template_file)
        fields = {
            'tenant_id' : tenant_id,
            'stack_name': stack_name,
            'parameters': params,
            'template': template,
            'files': dict(list(tpl_files.items())),
        }
	self.logger.debug(json.dumps(fields))
        r = requests.post(heat_base_url + "/" + tenant_id + "/stacks", data = json.dumps(fields), headers = headers)
        data = r.json()
	self.logger.debug("CREATE STACK DATA: %s", data)
        return data['stack']['id']
    
    def update_stack(self, token, tenant_id, heat_base_url, stack_name, stack_id, template_file, params):
        headers = {'X-Auth-Token': token}
        tpl_files, template = template_utils.get_template_contents(template_file = template_file)
        fields = {
            'tenant_id' : tenant_id,
            'stack_name': stack_name,
	    'stack_id' : stack_id,
            'parameters': params,
            'template': template,
            'files': dict(list(tpl_files.items())),
        }      
	r = requests.put(heat_base_url + "/" + tenant_id + "/stacks" + "/" + stack_name + "/" + stack_id, data = json.dumps(fields), headers=headers)
        return r.status_code

    def status_stack(self, token, tenant_id, heat_base_url, stack_name, stack_id):
        headers = {'X-Auth-Token': token}
        r = requests.get(heat_base_url + "/" + tenant_id + "/stacks/" + stack_name + "/" + stack_id, headers = headers)
        return r.json()

    def delete_stack(self, token, tenant_id, heat_base_url, stack_name, stack_id):
        headers = {'X-Auth-Token': token}
        r = requests.delete(heat_base_url + "/" + tenant_id + "/stacks/" + stack_name + "/" + stack_id, headers = headers)
        return r

if __name__ == "__main__":
   credentials = sys.argv[1]
   profile = sys.argv[2]

   cluster = OpenStackCloud(credentials, profile)

   cluster.allocate_resources()
   print cluster.getResources().getMachineFile()
   print cluster.getResources().runCommand("cat ~/machinefile")


      

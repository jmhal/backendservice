import json
import requests
import os
import yaml
import time
import logging
import uuid
import sys

from os import environ as env
from os import path as path
from datetime import datetime
from heatclient.common import template_utils

class OpenStackCloud:
    def __init__(self, credentials_filename, profile_filename):
        # Unique ID for this cluster
	self.deployment_id = uuid.uuid4()

        # credentials
	_dict = self.parse_rc(credentials_filename)
        self.username = _dict["OS_USERNAME"]
	self.password = _dict["OS_PASSWORD"]
	self.key_file = _dict["OS_KEYFILE"]
	self.auth_url = _dict["OS_AUTH_URL"]
        self.heat_base_url = "http://" + self.auth_url.split(":")[1][2:] + ":8004/v1"
	self.tenant_name = _dict["OS_TENANT_NAME"]
	self.region_name = _dict["OS_REGION_NAME"]

	# profile
	profile_file = open(profile_filename, "r")
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

    def deallocate_resources(self):
        """
        Destroy the stack.
        """
        self.authenticate()

        self.delete_stack(token = self.token, tenant_id = self.tenant_id , heat_base_url = self.heat_base_url ,
                          stack_name = self.stack_name, stack_id = self.stack_id)

        return "DESTROYED" 

    def getResources(self):
        pass

    def getClusterStatistics(self):
        pass

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

    def addNode(self, n = 1):
        return self.changeNodeNumber(n)
       
    def removeNode(self, n = 1):
        return self.changeNodeNumber(-n)
	
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
   # while cluster.allocation_status() != "READY":
   #    time.sleep(10)
   print "Stack Created..."
   # print "Type to increase the cluster in 1 ..."
   # wait = raw_input()
   print cluster.addNode(1)
   # print "Type to decrease the cluster in 2 ..."
   # wait = raw_input()
   print cluster.removeNode(2)
   # print "Type anything to destroy the stack..."
   # wait = raw_input()
   cluster.deallocate_resources()


      

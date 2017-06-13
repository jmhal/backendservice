import logging
import time
from keystone import Keystone
from heat import Heat

class OpenStack:
   def __init__(self, credentials):
      # credentials
      _dict = self.parse_rc(credentials)
      self.username = _dict["OS_USERNAME"]
      self.password = _dict["OS_PASSWORD"]
      self.key_file = _dict["OS_KEYFILE"]
      self.auth_url = _dict["OS_AUTH_URL"]
      self.heat_base_url = "http://" + self.auth_url.split(":")[1][2:] + ":8004/v1"
      self.tenant_name = _dict["OS_TENANT_NAME"]
      self.region_name = _dict["OS_REGION_NAME"]

      # keystone service
      self.keystone = Keystone(self.auth_url, self.tenant_name, self.username, self.password)

      # heat service
      self.heat = Heat(self.heat_base_url)

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

      return
   
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
       
   def deploy_profile(self, stack_name, template_file, params):
      """
      Deploy the template stack.
      """
        
      data = self.heat.create_stack(token = self.keystone.authenticate(), 
                                    tenant_id = self.keystone.tenant_id, 
                                    stack_name = stack_name, 
                                    template_file = template_file, 
                                    params = params)

      stack_id = data['stack']['id']

      while self.profile_status(stack_name, stack_id) == "BUILDING" :
         time.sleep(5)
       
      return stack_id

   def update_profile(self, stack_name, stack_id, template_file, params):
      """
      Deploy the template stack.
      """
        
      data = self.heat.update_stack(token = self.keystone.authenticate(), 
	                            tenant_id = self.keystone.tenant_id, 
                                    stack_name = stack_name, 
				    stack_id = stack_id,
	                            template_file = template_file, 
				    params = params)

      while self.profile_status(stack_name, stack_id) == "BUILDING" :
         time.sleep(5)
       
      return data 

   def profile_status(self, stack_name, stack_id):
      """
      How is the stack? 
      """
      data = self.heat.status_stack(token = self.keystone.authenticate(), 
	                            tenant_id = self.keystone.tenant_id, 
                                    stack_name = stack_name,
				    stack_id = stack_id)
        
      return self.results_status[data['stack']['stack_status']]

   def destroy_profile(self, stack_name, stack_id):
      """
      Destroy the stack.
      """

      self.heat.delete_stack(token = self.keystone.authenticate(),
	                     tenant_id = self.keystone.tenant_id , 
                             stack_name = stack_name, 
			     stack_id = stack_id)

      return "DESTROYED" 
      
   def get_ips(self, stack_name, stack_id):
      while self.profile_status(stack_name, stack_id) == "BUILDING" :
         time.sleep(10)

      data = self.heat.status_stack(token = self.keystone.authenticate(), 
	                            tenant_id = self.keystone.tenant_id, 
                                    stack_name = stack_name, 
				    stack_id = stack_id)

      outputs = data['stack']['outputs']

      ips = {}
      for d in outputs:
         ips[d['output_key']] = d['output_value']
      return ips



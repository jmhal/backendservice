import json
import requests
import logging
from heatclient.common import template_utils

class Heat:
   def __init__(self, heat_base_url):
      self.heat_base_url = heat_base_url    

      # configure logging
      logging.basicConfig(level=logging.DEBUG)
      self.logger = logging.getLogger(__name__)

      return

   def create_stack(self, token, tenant_id, stack_name, template_file, params):
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
      r = requests.post(self.heat_base_url + "/" + tenant_id + "/stacks", data = json.dumps(fields), headers = headers)
      data = r.json()
      self.logger.debug("CREATE STACK DATA: %s", data)
      return data #['stack']['id']
    
   def update_stack(self, token, tenant_id, stack_name, stack_id, template_file, params):
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
      r = requests.put(self.heat_base_url + "/" + tenant_id + "/stacks" + "/" + stack_name + "/" + stack_id, data = json.dumps(fields), headers=headers)
      self.logger.debug("UPDATE STACK DATA: %s", r)
      return r.status_code

   def status_stack(self, token, tenant_id, stack_name, stack_id):
      headers = {'X-Auth-Token': token}
      r = requests.get(self.heat_base_url + "/" + tenant_id + "/stacks/" + stack_name + "/" + stack_id, headers = headers)
      data = r.json()
      self.logger.debug("STATUS STACK DATA: %s", data)
      return data #['stack']['stack_status']

   def delete_stack(self, token, tenant_id, stack_name, stack_id):
      headers = {'X-Auth-Token': token}
      r = requests.delete(sel.fheat_base_url + "/" + tenant_id + "/stacks/" + stack_name + "/" + stack_id, headers = headers)
      data = r.json()
      self.logger.debug("DELETE STACK DATA: %s", data)
      return data

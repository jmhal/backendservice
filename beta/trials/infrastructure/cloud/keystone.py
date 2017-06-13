import json
import requests
import time
import logging
from datetime import datetime

class Keystone:
   def __init__(self, auth_url, tenant_name, username, password):
      self.auth_url = auth_url
      self.url = auth_url + "/tokens"
      self.tenant_name = tenant_name
      self.username = username
      self.password = password

      self.token_create_time = datetime.now()
      self.token = self.get_auth_token(self.tenant_name, self.username, self.password)
      self.tenant_id = self.get_tenant_id(self.tenant_name)

      # configure logging
      logging.basicConfig(level=logging.DEBUG)
      self.logger = logging.getLogger(__name__)

      return

   def authenticate(self):
      """
      Create a token for the heat API calls.
      """
      now = datetime.now()
      difference = now - self.token_create_time
      if difference.seconds > 60 * 60:
         self.token = self.get_auth_token(self.url, self.tenant_name, self.username, self.password)
      return self.token

   def get_auth_token(self, tenant_name, username, password):
      headers = {'Content-Type':'application/json'}
      fields = {
         'auth':{
            'tenantName': tenant_name,
            'passwordCredentials':{
               'username': username,
               'password': password}
             }
      }
      r = requests.post(self.url, data = json.dumps(fields), headers = headers)
      token_id = r.json()['access']['token']['id']
      return token_id

   def get_tenant_id(self, tenant_name):
      headers = {'X-Auth-Token': self.authenticate()}
      r = requests.get(self.auth_url + "/tenants", headers=headers)
      json = r.json()
      for element in json['tenants']:
         if element['name'] == tenant_name:
             return element['id']
      return None



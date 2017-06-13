:
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
      self.keystone = Keystone(self.auth_url, self_tenant_name, self.username, self.password)

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
       
    def allocate_resources(self):
        """
        Deploy the template stack.
        """
        self.authenticate()

	if self.stack_id != None:
	   return self.stack_id
        
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



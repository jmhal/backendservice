
class Cluster():
   def __init__(self, credentials, profile, stack_id, stack_name):
      # openstack services
      self.openstack = OpenStack(credentials)

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
      
      # stack name and stack id
      self.stack_id = stack_id
      self.stack_name = stack_name
     
      # ssh setup
      self.username = "ubuntu"
      self.port = 22
      self.ssh = paramiko.SSHClient()

    def run_command(self, cmd):
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
 
    def configure_machine_file(self):
       machinefile = open("~/machinefile", "w")
       machinefile.write(self.ips['head_node_ip'] + ":" + str(self.cores))
       for machine in self.ips['compute_node_ips']:
          machinefile.write(machine + ":" + str(self.cores))
       machinefile.close()
       return 

    def addNode(self, n = 1):
       return self.changeNodeNumber(n)
       
    def removeNode(self, n = 1):
        return self.changeNodeNumber(-n)

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



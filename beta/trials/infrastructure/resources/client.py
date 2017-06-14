import xmlrpclib

class ResourcesProxy():
   def __init__(self, url, stack_name, stack_id):
      self.proxy = xmlrpclib.ServerProxy(url)      

   def addNode(self, n = 1):
      return self.proxy.add_node(self.stack_name, self.stack_id, n) 
       
   def removeNode(self, n = 1):
      return self.proxy.remove_node(self.stack_name, self.stack_id, n) 

   def getResourceState(self):
      pass 

   def configure_machine_file(self):
      machinefile = open(os.environ['HOME'] + "/machinefile", "w")
      
      ips = self.proxy.get_ips(self.stack_name, self.stack_id)
      
      self.number_of_nodes = 1
      machinefile.write(ips['head_node_ip'] + ":" + str(self.cores))
      for machine in ips['compute_node_ips']:
         machinefile.write(machine + ":" + str(self.cores))
	 self.number_of_nodes += 1
      machinefile.close()
      
      return self.number_of_nodes



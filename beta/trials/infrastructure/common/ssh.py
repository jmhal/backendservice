import paramiko

class SSH:
   def __init__(self, username, keyfile, port):
      self.username = username 
      self.keyfile = keyfile
      self.port = 22
      self.ssh = paramiko.SSHClient()

   def run_command(self, ip, cmd):
      self.connect(ip)
      ssh_stdin, ssh_stdout, ssh_stderr = self.ssh.exec_command(cmd)
      output = ""
      for line in ssh_stdout.readlines():
           output = output + line
      self.disconnect()
      return output

   def copy_file(self, ip, _file, name):
      self.connect(ip)
      sftp = self.ssh.open_sftp()
      sftp.put(_file, "/home/ubuntu/" + name);
      sftp.close()
      self.disconnect()

   def connect(self, ip):
      self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
      self.ssh.connect(ip, self.port, username=self.username, key_filename=self.keyfile)

   def disconnect(self):
      self.ssh.close()
 
     

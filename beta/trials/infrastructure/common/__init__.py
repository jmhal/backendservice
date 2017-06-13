import yaml

def parse_profile(profile):
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



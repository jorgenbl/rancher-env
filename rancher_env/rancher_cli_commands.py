import subprocess
import os
import glob
import json
import time
from shutil import copyfile
from beautifultable import BeautifulTable

def get_environments():
    '''
    Gets environments in current configuration
    '''
    proc = subprocess.Popen(['rancher', 'env', 'ls', '--format', 'json'],stdout=subprocess.PIPE)
    output, error = proc.communicate()
    lines = output.splitlines()
    result = []
    for line in lines:
        result.append(line.decode("utf-8"))
    return result

def get_containers():
    '''
    Gets the containers in the current configuration
    '''
    proc = subprocess.Popen(['rancher', 'ps', '--format', 'json'],stdout=subprocess.PIPE)
    output, error = proc.communicate()
    lines = output.splitlines()
    result = []
    for line in lines:
        result.append(line.decode("utf-8"))
    return result

def get_containers_advanced(environment, url, accesskey, secretkey):
    '''
    Gets the containers in the current configuration
    '''
    proc = subprocess.Popen(['rancher', '--url', url, '--access-key', accesskey, '--secret-key', secretkey, '-env', environment, 'ps', '--format', 'json'],stdout=subprocess.PIPE)
    output, error = proc.communicate()
    lines = output.splitlines()
    result = []
    for line in lines:
        result.append(line.decode("utf-8"))
    return result

def tablefy_environments(table, environments):
    for environment in environments:
        row = []
        row.append(environment["Environment"]["id"])
        row.append(environment["Environment"]["name"])
        row.append(environment["Environment"]["orchestration"])
        row.append(environment["Environment"]["state"])
        row.append(environment["Environment"]["created"])
        row.append(environment["url"])
        table.append_row(row)
    return table

def tablefy_containers(table, containers):
    for container in containers:
        row = []
        row.append(container["ID"])
        row.append(container["Service"]["type"])
        row.append(container["Name"])
        image = "N/A"
        #stack = container["Stack"]
        #if "dockerCompose" in stack:
        #    dockerCompose = stack["dockerCompose"].split("\n")
        #    for line in dockerCompose:
        #        if "image" in line:
        #            image = line.split(":")[1].strip()
        #            break
        try:
            image = container["Service"]["launchConfig"]["imageUuid"]
        except:
            print("not found")
        row.append(image)
        row.append(container["Service"]["state"])
        try:
            nContainers = len(container["Service"]["instanceIds"])
            scale = container["Service"]["scale"]
            row.append(str(nContainers)+"/"+str(scale))
        except:
            row.append("N/A")
        row.append("N/A")
        row.append("N/A")
        row.append("N/A")
        row.append(container["env"])
        row.append(container["url"])
        table.append_row(row)
    return table

def get_current_config():
    '''
    Get the current rancher cli config
    '''
    proc = subprocess.Popen(['rancher', 'config', '--print'],stdout=subprocess.PIPE)
    output, error = proc.communicate()
    data = json.loads(output)
    return data

def remove_config(config_path):
    '''
    Removes a config based on config_path parameter
    '''
    os.remove(config_path)


def get_saved_configs():
    '''
    Get all configs from .rancher-env
    '''
    result = []
    rancher_env_dir = get_confdir()
    path = rancher_env_dir + "/*.json"
    files=glob.glob(path)   
    for file in files:     
        with open(file) as data_file:    
            data = json.load(data_file)
        data["path"] = file
        result.append(data)
    return result


def list_all_containers():
    containers = get_all_containers()
    #for container in containers:
    #    print(container["Stack"]["dockerCompose"])

    table = BeautifulTable(max_width=200, default_alignment=BeautifulTable.ALIGN_LEFT)
    table.width_exceed_policy = BeautifulTable.WEP_ELLIPSIS
    table.column_headers = ["ID", "TYPE", "NAME", "IMAGE", "STATE", "SCALE", "SYSTEM", "ENDPOINTS", "DETAIL", "ENVIRONMENT", "URL"]
    table.left_border_char = ''
    table.right_border_char = ''
    table.top_border_char = ''
    table.bottom_border_char = ''
    table.header_seperator_char = ''
    table.row_seperator_char = ''
    table.intersection_char = ''
    table.column_seperator_char = ''
    # # table.right_padding_widths['NAME'] = 2
    # # table.right_padding_widths['ORCHESTRATION'] = 2
    # # table.right_padding_widths['STATE'] = 3

    tablefy_containers(table,containers)

    # Print final table
    print(table)

def get_all_containers():
    '''
    Function that gets all the containers/servises and returns them structured
    '''

    environments = get_all_environments()        
    current_config = get_current_config()
    saved_configs = get_saved_configs()
    containers = []

    for environment in environments:
        config = {}
        if environment["url"] == current_config["url"]:
            config = current_config
        else:
            for saved_config in saved_configs:
                if environment["url"] == saved_config["url"]:
                    config = saved_config
                    break
        for container in get_containers_advanced(environment["ID"], environment["url"], config["accessKey"], config["secretKey"]):
            container = json.loads(container)
            container["env"] = environment["ID"]
            container["url"] = environment["url"]
            containers.append(container) 

    return containers

def get_all_environments():
    '''
    Function that gets all the environments and returns them structured
    '''

    current_config = get_current_config()
    saved_configs = get_saved_configs()
    environments = []
    # First check if current config is one of the saved ones
    current_saved = False
    for config in saved_configs:
        if config["url"] == current_config["url"]:
            current_saved = True
    if not current_saved:
        for env in get_environments():
            env = json.loads(env)
            env["url"] = current_config["url"]
            environments.append(env)
    # Backup current config, and remove it
    current_config_file_exists = True
    if os.path.isfile(current_config["path"]):
        os.rename(current_config["path"], current_config["path"] + ".bak")
    else:
        current_config_file_exists = False
        

    # Iterate each saved config
    for config in saved_configs:
        copyfile(config["path"], current_config["path"])
        for env in get_environments():
            env = json.loads(env)
            env["url"] = config["url"]
            environments.append(env)
        os.remove(current_config["path"])

    # Revert to old config if exists
    if current_config_file_exists:
        os.rename(current_config["path"] + ".bak", current_config["path"])

    # Return all environments
    return environments

def list_all_environments():
    '''
    List all environments in .rancher and .rancher-env
    '''

    table = BeautifulTable(max_width=160, default_alignment=BeautifulTable.ALIGN_LEFT)
    table.column_headers = ["ID", "NAME", "ORCHESTRATION", "STATE", "CREATED", "URL"]
    table.left_border_char = ''
    table.right_border_char = ''
    table.top_border_char = ''
    table.bottom_border_char = ''
    table.header_seperator_char = ''
    table.row_seperator_char = ''
    table.intersection_char = ''
    table.column_seperator_char = ''
    # table.right_padding_widths['NAME'] = 2
    # table.right_padding_widths['ORCHESTRATION'] = 2
    # table.right_padding_widths['STATE'] = 3

    environments = get_all_environments()
    tablefy_environments(table,environments)

    # Print final table
    print(table)


def create_config(name):
    '''
    Save a config based on the current. Will check if config already exists based on url. 
    If not prefix with name, and save to .rancher-env folder. If no name specified, timestamp is used.
    '''

    current_config = get_current_config()
    saved_configs = get_saved_configs()

    # First check if current config is one of the saved ones
    current_saved = False
    current_saved_config = ""
    for config in saved_configs:
        if config["url"] == current_config["url"]:
            current_saved = True
            current_saved_config = config
    if not current_saved:
        if os.path.isfile(current_config["path"]):
            confdir = get_confdir()
            if name:
                os.rename(current_config["path"], confdir + "/" + name + ".cli.json")
            else:
                timestamp = int(time.time())
                os.rename(current_config["path"], confdir + "/" + str(timestamp) + ".cli.json")
        else:
            print("No current config to save, please create one first with 'rancher config'")
    else:
        print("The config is already saved as: {}".format(current_saved_config["path"]))


def switch_config(config_path):
    '''
    Overwrite current config with config specified in config_path
    Will check if current config exists in saved config directory, if not save with a timestamp
    '''

    current_config = get_current_config()
    saved_configs = get_saved_configs()

    # First check if current config is one of the saved ones
    current_saved = False
    for config in saved_configs:
        if config["url"] == current_config["url"]:
            current_saved = True
    if not current_saved:
        timestamp = int(time.time())
        confdir = get_confdir()
        if os.path.isfile(current_config["path"]): 
            os.rename(current_config["path"], confdir + "/" + str(timestamp) + ".cli.json")
        
    # Set new config    
    copyfile(config_path, current_config["path"])


def list_configs():
    '''
    List configuration files stored in .rancher-env folder and current config if exists
    '''

    # First current config
    current_config = get_current_config()
    if os.path.isfile(current_config["path"]):
        print(current_config)
    rancher_env_dir = get_confdir()

    # Then saved configs
    path = rancher_env_dir + "/*.json"
    files=glob.glob(path)   
    for file in files:     
        with open(file) as data_file:    
            data = json.load(data_file)
        data["path"] = file
        print(json.dumps(data))

def get_confdir():
    '''
    Returns os spesific configuration dir
    '''
    return os.path.expanduser("~") + "/.rancher-env"

def get_current_confdir():
    '''
    Returns os spesific configuration dir
    '''
    return os.path.expanduser("~") + "/.rancher"

def make_confdir():
    '''
    Create configuration directory if not already existing
    '''
    rancher_env_dir = get_confdir()
    os.makedirs(rancher_env_dir, mode=0o700, exist_ok=True)
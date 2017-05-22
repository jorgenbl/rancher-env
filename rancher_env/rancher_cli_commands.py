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
    proc = subprocess.Popen(['rancher', 'env', 'ls'],stdout=subprocess.PIPE)
    output, error = proc.communicate()
    lines = output.splitlines()
    result = []
    counter = 0
    for line in lines:
        if not counter == 0:
            result.append(line.decode("utf-8"))
        counter += 1
    return result

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


def list_all_environments():
    '''
    List all environments in .rancher and .rancher-env
    '''

    table = BeautifulTable(max_width=160, default_alignment=BeautifulTable.ALIGN_LEFT)
    #table = BeautifulTable(default_alignment=BeautifulTable.ALIGN_LEFT)
    #table.width_exceed_policy = BeautifulTable.WEP_WRAP
    #table.auto_calculate_width()
    table.column_headers = ["URL", "ID", "NAME", "ORCHESTRATION", "STATE", "CREATED"]

    current_config = get_current_config()
    saved_configs = get_saved_configs()

    # First check if current config is one of the saved ones
    current_saved = False
    for config in saved_configs:
        if config["url"] == current_config["url"]:
            current_saved = True
    if not current_saved:
        environments = get_environments()
        for environment in environments:
            row = [current_config['url']] + environment.split()
            table.append_row(row)

    # Backup current config, and remove it
    current_config_file_exists = True
    if os.path.isfile(current_config["path"]):
        os.rename(current_config["path"], current_config["path"] + ".bak")
    else:
        current_config_file_exists = False
        

    # Iterate each saved config
    for config in saved_configs:
        copyfile(config["path"], current_config["path"])
        environments = get_environments()
        for environment in environments:
            row = [config['url']] + environment.split()
            table.append_row(row)
        os.remove(current_config["path"])

    # Print final table
    print(table)

    # Revert to old config if exists
    if current_config_file_exists:
        os.rename(current_config["path"] + ".bak", current_config["path"])



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
                os.rename(current_config["path"], confdir + "/" + timestamp + ".cli.json")
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
        os.rename(current_config["path"], confdir + "/" + timestamp + ".cli.json")

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


def main():
    #list_environments()
    #make_confdir()
    #list_configs()
    list_all_environments()
    #switch_config("/Users/jblakstad/.rancher-env/lab-cli.json")

if __name__ == "__main__":
    main()
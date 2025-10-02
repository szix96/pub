import os
from netmiko import ConnectHandler
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

def load_env_vars(filepath=".env"):
    try:
        with open(filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip().strip('"\'')
                    os.environ[key] = value
    except FileNotFoundError:
        print(f"{filepath}no file found make sure there is .env")

def load_devices_from_yaml(filepath="devices.yaml"):

    devices = []
    try:
       with open(filepath, 'r') as f:
         lines = f.readlines()
    except FileNotFoundError:
        print(f"Error no devices file at {filepath}")
        return devices

    current_device = None
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith('#') or stripped == 'devices:':
            continue
        if stripped.startswith('-'):
            if current_device:
                devices.append(current_device)
            current_device = {}
            rest_of_line = stripped[1:].strip()
            if ':' in rest_of_line:
                key, value = rest_of_line.split(':', 1)
                current_device[key.strip()] = value.strip()
        elif current_device is not None and ':' in stripped:
            key, value = stripped.split(':', 1)
            current_device[key.strip()] = value.strip()
    
    if current_device:
        devices.append(current_device)

    return devices

load_env_vars()

password = os.getenv("MANAGER_PASSWORD")
enable_secret = os.getenv("ENABLE_SECRET")

if not password or not enable_secret:
    print("no password/enable defined")
    exit()

devices = load_devices_from_yaml()

if not devices:
    print(" no deivces defined in file")
    exit()

for device in devices:
    device['password'] = password
    device['secret'] = enable_secret
    device['ssh_config_file'] = './ssh_config'

for device in devices:
    hostname = device.pop('hostname', device.get('host'))

    try:
        with ConnectHandler(**device) as net_connect:
            net_connect.enable()
            output = net_connect.send_command('show running-config', read_timeout=20)

            filename = f"{hostname}_running_config.txt"
            with open(filename, 'w') as f:
                f.write(output)
            print(f"--- Running config for {device['host']} ({hostname}) saved to {filename} ---")
    
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
        print(f"failed to connect to {device['host']} ({hostname}): {e}")
    except Exception as e:
        print(f"An error occured at {device['host']} ({hostname}): {e}")
    

            






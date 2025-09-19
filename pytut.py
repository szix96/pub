import sys
print(f"--- Running script: {sys.argv[0]} ---", flush=True)

# Import the 'os' library to interact with the operating system, for reading environment variables.
import os
# Import the main connection handler from the Netmiko library.
from netmiko import ConnectHandler
# Import specific Netmiko exceptions to handle them gracefully.
from netmiko.exceptions import NetmikoTimeoutException, NetmikoAuthenticationException

# Defines a function named load_env_vars that accepts a file path, defaulting to ".env".
def load_env_vars(filepath=".env"):
    """
    Manually loads environment variables from a .env file.
    This is a simplified parser and may not handle all cases.
    """
    # Start a 'try' block to gracefully handle potential errors, like a missing file.
    try:
        # Open the specified file in read-only mode ('r').
        with open(filepath, 'r') as f:
            # Start a loop that reads the file one line at a time.
            for line in f:
                # For each line, remove any leading or trailing whitespace (spaces, newlines).
                line = line.strip()
                # Process the line only if it's not empty, not a comment, and contains an '='.
                if line and not line.startswith('#') and '=' in line:
                    # Split the line into two parts at the first '=' sign found.
                    key, value = line.split('=', 1)
                    # Clean up the key by removing any extra whitespace around it.
                    key = key.strip()
                    # Clean up the value by first removing whitespace, then removing any surrounding quotes.
                    value = value.strip().strip('"\'")
                    # Add the cleaned key and value to the script's environment variables.
                    os.environ[key] = value
    # If the file was not found in the 'try' block, this code will run.
    except FileNotFoundError:
        # Print a warning message instead of crashing the script.
        print(f"Warning: {filepath} not found. Cannot load environment variables.")

# Defines a function named load_devices_from_yaml that accepts a file path, defaulting to "devices.yaml".
def load_devices_from_yaml(filepath="devices.yaml"):
    """
    Manually parses a simple YAML file for a list of devices.
    This is a very basic parser and is not robust.
    It expects a specific format as created in the previous step.
    """
    # Initialize an empty list to store the device dictionaries we find.
    devices = []
    # Start a 'try' block to handle a missing file.
    try:
        # Open the file and read all lines into a list of strings.
        with open(filepath, 'r') as f:
            lines = f.readlines()
    # If the file doesn't exist, print an error and return the empty list.
    except FileNotFoundError:
        print(f"Error: {filepath} not found.")
        return devices

    # Initialize a state variable to hold the device dictionary currently being built.
    current_device = None
    # Loop through each line that was read from the file.
    for line in lines:
        # Get a clean version of the line with no leading/trailing whitespace.
        stripped = line.strip()
        # If the line is empty, a comment, or the 'devices:' header, skip to the next line.
        if not stripped or stripped.startswith('#') or stripped == 'devices:':
            continue

        # Check if the line marks the beginning of a new device (starts with '-').
        if stripped.startswith('-'):
            # If we were already building a device, add the completed device to our list first.
            if current_device:
                devices.append(current_device)
            # Reset current_device to a new empty dictionary for the new device.
            current_device = {}
            # Get the part of the string after the '-' to handle same-line key-value pairs.
            rest_of_line = stripped[1:].strip()
            # If a ':' exists on the same line, parse it as the first key-value pair.
            if ':' in rest_of_line:
                key, value = rest_of_line.split(':', 1)
                current_device[key.strip()] = value.strip()
        # If this is a normal indented line (not starting with '-'), process it.
        elif current_device is not None and ':' in stripped:
            # Split the line at the colon to get the key and value.
            key, value = stripped.split(':', 1)
            # Add the cleaned key-value pair to the device dictionary we are currently building.
            current_device[key.strip()] = value.strip()
    
    # After the loop finishes, append the very last device to the list.
    if current_device:
        devices.append(current_device)
    
    # Return the final list of device dictionaries.
    return devices

# --- Main Script ---

# Load the credentials from the .env file into the script's environment.
load_env_vars()
# Retrieve the manager password from the environment variables.
password = os.getenv("MANAGER_PASSWORD")
# Retrieve the enable secret from the environment variables.
enable_secret = os.getenv("ENABLE_SECRET")

# If either the password or the secret was not found, print an error and exit the script.
if not password or not enable_secret:
    print("Error: MANAGER_PASSWORD and ENABLE_SECRET must be set in the .env file.")
    exit()

# Load the device inventory from the devices.yaml file.
devices = load_devices_from_yaml()

# If no devices were loaded, print an error and exit the script.
if not devices:
    print("Error: No devices found in devices.yaml or the file is not in the expected format.")
    exit()


# Prepare the device list for connection by adding credentials to each device.
for device in devices:
    # Add the global password to the current device's dictionary.
    device['password'] = password
    # Add the global enable secret to the current device's dictionary.
    device['secret'] = enable_secret
    # Add the path to the SSH config file to handle legacy algorithms.
    device['ssh_config_file'] = './ssh_config'

# Main loop to connect to each device and retrieve its configuration.
for device in devices:
    # Get the hostname for display purposes, falling back to the host IP if not present.
    hostname = device.pop('hostname', device.get('host'))
    # Start a 'try' block to handle any network or authentication errors gracefully.
    try:
        # Print a status message to the screen.
        print(f"Connecting to {device['host']} ({hostname})...")
        # Establish the SSH connection using all parameters in the 'device' dictionary.
        # The 'with' statement ensures the connection is automatically closed.
        with ConnectHandler(**device) as net_connect:
            # Enter privileged (enable) mode on the device.
            net_connect.enable()
            # Send the 'show running-config' command and store the output.
            output = net_connect.send_command('show running-config', read_timeout=20)
            
            # Display the device config on screen.
            print("--- DEBUGGING INFO ---", flush=True)
            print(f"Type of output: {type(output)}", flush=True)
            print(f"Repr of output: {repr(output)}", flush=True)
            print("--- DEVICE CONFIGURATION ---", flush=True)
            print(output, flush=True)
            print("--- END OF CONFIGURATION ---", flush=True)
            
            # Define a filename for the output based on the device's hostname.
            filename = f"{hostname}_running_config.txt"
            # Open the new file in write mode ('w').
            with open(filename, 'w') as f:
                # Write the captured configuration output to the file.
                f.write(output)
            # Print a success message indicating the file has been saved.
            print(f"--- Running config for {device['host']} ({hostname}) saved to {filename} ---")

    # If a timeout or authentication error occurs, catch it and print a specific message.
    except (NetmikoTimeoutException, NetmikoAuthenticationException) as e:
        print(f"Failed to connect to {device['host']} ({hostname}): {e}")
    # Catch any other general errors that might occur.
    except Exception as e:
        print(f"An error occurred with {device['host']} ({hostname}): {e}")

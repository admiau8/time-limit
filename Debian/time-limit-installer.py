#!/usr/bin/python3

import subprocess       # For running system commands
import os               # For interacting with the operating system
import configparser     # For parsing configuration files

# Function to authenticate the user as root and protect the desktop entry file
def authenticate():
    # Define the desktop file path
    desktop_file_path = os.path.join(autostart_dir, "time-limit.desktop")

    # Check if the desktop file exists; if not, create it with appropriate content
    if not os.path.exists(desktop_file_path):
        with open(desktop_file_path, 'w') as f:
            f.write("[Desktop Entry]\nName=Print Service\nExec=time-limit-service.py\nType=Application\n")
        print(f"{desktop_file_path} created with default content")

    # Protect the desktop file using 'pkexec' and 'chattr'
    result = subprocess.run(
        ["pkexec", "sh", "-c", f"chattr +i {desktop_file_path} && whoami"],
        capture_output=True,
        text=True
    )

    # Check command success and output results
    if result.returncode == 0:
        print("Desktop file protected and command output:", result.stdout.strip())  # Strip any trailing newlines
    else:
        print("Error:", result.stderr)  # Print the error output if the command fails

    # Confirm if the user is root; exit if authentication fails
    if result.stdout.strip() != "root":
        exit("Authentication failed")

# Function to execute shell commands efficiently
def cmd(command):
    try:
        # Run the command asynchronously
        subprocess.Popen(command, shell=True)
    except Exception as e:
        print(f"Error executing command {command}: {e}")

# Start the script's main operations

# Retrieve the current user's home directory path
home_dir = os.path.expanduser("~")

print("Starting time-limit...")

# Define paths for config and autostart files
config_file = os.path.join(home_dir, '.time-limit-config.ini')
autostart_dir = os.path.join(home_dir, ".config/autostart")

# Ensure the autostart directory exists
os.makedirs(autostart_dir, exist_ok=True)

# Authenticate the user and protect the desktop entry file
authenticate()

# Create the initial configuration file if it does not exist
if not os.path.exists(config_file):
    with open(config_file, 'w') as f:
        f.write("[Time-Limit]\nlocktime=23.0\nmorning=6.0\n")
print("Config file checked or created")

# Create a fake shortcut for distraction
fake_shortcut_path = os.path.join(autostart_dir, "time-limit-fake.desktop")
with open(fake_shortcut_path, 'w') as f:
    f.write("[Desktop Entry]\nName=Time limit\nExec=whoami\nType=Application\n")
os.chmod(fake_shortcut_path, 0o755)
print(f"{fake_shortcut_path} has been created")

# Get locktime and morning time via zenity dialogs
locktime, morning = None, None
for title, default_value, var_name in [("מהי-שעת-הנעילה?", 23, 'locktime'), ("מתי-בוקר?", 6, 'morning')]:
    command = f"zenity --scale --text={title} --value={default_value} --min-value=0 --max-value=23 --step=1"
    try:
        result = subprocess.check_output(command, shell=True, text=True).strip()
        if var_name == 'locktime':
            locktime = float(result)
        elif var_name == 'morning':
            morning = float(result)
        print(f"{var_name.capitalize()} set to {result}")
    except subprocess.CalledProcessError:
        print(f"User canceled {var_name}")

# Create ConfigParser object to interact with the config file
config = configparser.ConfigParser()
config.read(config_file)

# Update configuration settings based on received values
if locktime is not None:
    config['Time-Limit']['locktime'] = str(locktime)  # Update locktime
if morning is not None:
    config['Time-Limit']['morning'] = str(morning)    # Update morning time

# Write updated configuration back to the file if any setting was modified
if locktime is not None or morning is not None:
    with open(config_file, 'w') as configfile:
        config.write(configfile)
    print("Configuration file updated")

# Start the time-limit service script
cmd('time-limit-service.py')
#!/usr/bin/python3

import subprocess  # For running system commands
import os          # For interacting with the operating system
import sys         # For system-specific parameters and functions
import time        # For handling time-related tasks
import re          # For regular expressions
import configparser  # For parsing configuration files

print("Starting time-limit-service...")

def cmd(command):
    try:
        os.system(command + ' &')
    finally:
        exitfinally = 1

#create config file
cmd('set -e; HOME_DIR="$HOME/"; CONFIG_FILE="$HOME_DIR/.time-limit-config.ini"; [ ! -f "$CONFIG_FILE" ] && printf "[Time-Limit]\\nlocktime=23.0\\nmorning=6.0\\n" > "$CONFIG_FILE"')
print("Config file created")

# Get the current user's home directory
home_dir = os.path.expanduser("~")

# Define the path to the time-limit-config.ini file located in the user's home directory
config_file = os.path.join(home_dir, '.time-limit-config.ini')

# Create a ConfigParser object to manage the configuration file
config = configparser.ConfigParser()

# Read the configuration file
config.read(config_file)

# Default values for morning and lock times
morning = 7.0  # Default start time of allowed use (7:00 AM)
locktime = 23.0  # Default lock time (11:00 PM), should be less than 24.00

# Override the default times with values from the configuration file
locktime = float(config['Time-Limit']['locktime'])
morning = float(config['Time-Limit']['morning'])

#print(f"Time limit is set from {start_time} to {end_time}")

def getTime():
    """
    Get the current time in hours and minutes as a float.

    Returns:
        float: Current time formatted as a float (e.g., 7.25 for 7:15).
    """
    current_time = time.strftime("%H:%M:%S")  # Get current time in HH:MM:SS format
    # Split the current time into hours and minutes
    mylist = re.split(':', current_time)
    minute = float(mylist[1])  # Get the current minute
    hour = float(mylist[0])    # Get the current hour
    timenow = hour + minute / 100  # Convert to float format (e.g., 7.25)
    print(timenow)  # Print the current time
    return timenow  # Return the current time


def isbetween(a, b):
    """
    Check if the current time is between two times a and b, accounting for times that cross midnight.
    
    Args:
        a (float): Start time in 24-hour float format (e.g., 1.0 for 1 AM).
        b (float): End time in 24-hour float format (e.g., 7.0 for 7 AM).
    
    Returns:
        bool: True if the current time is between a and b, otherwise False.
    """
    current_time = getTime()
    
    # If a < b, the range does not cross midnight, simple comparison
    if a < b:
        return a <= current_time <= b
    else:
        # Range crosses midnight, check if the current time is after 'a' or before 'b'
        return current_time >= a or current_time <= b










def lockuntil(end):
    """
    Lock the screen until the specified time.

    Args:
        end (float): The time until which the screen should remain locked.
    """
    while isbetween(locktime,morning):
            cmd('wmctrl -k on')  # Minimize all windows
            cmd('mate-screensaver-command --lock')  # Lock the screen
            cmd('gnome-screensaver-command --lock')  # Lock the screen
            
            print("locked until " + str(morning))  # Indicate that the screen is locked
            time.sleep(0.2)  # Wait for 0.2 seconds before re-checking
    print("unlocked")  # Indicate that the screen has been unlocked




# Start of the program
print('locktime is ' + str(locktime))  # Display the configured lock time
print('morning is ' + str(morning))    # Display the configured morning time
cmd('zenity --info --text="הגבלת זמן פעילה"')  # Show a notification that time restrictions are active


# Main loop to enforce the time limit
while True:
    print("Waiting until" + str(locktime))  # Indicate that the program is waiting within the allowed time
    # Check if the current time is within the allowed range before locking

    while isbetween(morning,locktime):
        #the real shortcut is called print service for confusing
        cmd('set -e; echo "Setting Start at login..."; AUTOSTART_DIR="$HOME/.config/autostart"; mkdir -p "$AUTOSTART_DIR"; DESKTOP_FILE="$AUTOSTART_DIR/time-limit.desktop"; printf "[Desktop Entry]\\nName=Print service\\nExec=time-limit-service.py\\nType=Application\\n" > "$DESKTOP_FILE"; chmod +x "$DESKTOP_FILE"; echo "time-limit.desktop has been created in $AUTOSTART_DIR"')
        time.sleep(5)  # Wait for 5 seconds before re-checking the time

    # Once outside the allowed time range, start locking actions
    cmd('wmctrl -k on')  # Minimize all windows
    time.sleep(2)
    cmd('zenity --warning --text="המחשב יינעל בעוד דקה"')  # Show a warning notification that the screen will lock in 1 minute
    time.sleep(60)
    
    # Lock the screen until the next allowed time (morning)
    lockuntil(morning)

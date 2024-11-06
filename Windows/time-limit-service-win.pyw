#!/usr/bin/python3

import os          # For interacting with the operating system
import time        # For handling time-related tasks
import re          # For regular expressions
import configparser  # For parsing configuration files

print("Starting time-limit-service...")

# Create config file if it doesn't exist
home_dir = os.path.expanduser("~")
config_file = os.path.join(home_dir, '.time-limit-config.ini')



if not os.path.exists(config_file):
    with open(config_file, 'w') as f:
        f.write("[Time-Limit]\n")
        f.write("locktime = 23.0\n")
        f.write("morning = 6.0\n")
    print("Config file created with default settings.")

# Create a ConfigParser object to manage the configuration file
config = configparser.ConfigParser()
config.read(config_file)

print("Available sections:", config.sections())

# Default values for morning and lock times
morning = 7.0  # Default start time of allowed use (7:00 AM)
locktime = 23.0  # Default lock time (11:00 PM), should be less than 24.00

# Override the default times with values from the configuration file
try:
    locktime = float(config['Time-Limit']['locktime'])
    morning = float(config['Time-Limit']['morning'])
except KeyError as e:
    print(f"Error: The section '{e}' is missing in the config file.")

def getTime():
    current_time = time.strftime("%H:%M:%S")
    mylist = re.split(':', current_time)
    minute = float(mylist[1])
    hour = float(mylist[0])
    timenow = hour + minute / 100
    print(timenow)
    return timenow

def isbetween(a, b):
    current_time = getTime()
    if a < b:
        return a <= current_time <= b
    else:
        return current_time >= a or current_time <= b

def lockuntil(end):
    while isbetween(locktime, morning):
        # Lock the screen
	# Minimize all windows
        os.system('powershell -command "(New-Object -ComObject shell.application).minimizeall()"')
        
        # Lock the screen
        os.system('rundll32.exe user32.dll,LockWorkStation')
        print("Locked until " + str(morning))
        time.sleep(0.2)
    print("Unlocked")

print('locktime is ' + str(locktime))
print('morning is ' + str(morning))

# Main loop to enforce the time limit
os.system('start cmd /c mshta vbscript:Execute("msgbox ""הגבלת זמן פעילה"":close")')

while True:
    print("Waiting until" + str(locktime))
    while isbetween(morning, locktime):
        time.sleep(5)

    print("The computer will lock in one minute")
    os.system('powershell -command "(New-Object -ComObject shell.application).minimizeall()"')
    time.sleep(2)
    os.system('start cmd /c mshta vbscript:Execute("msgbox ""המחשב יינעל בעוד דקה"":close")')
    time.sleep(60)
    lockuntil(morning)

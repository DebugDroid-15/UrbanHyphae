#!/usr/bin/env python3
import os
import sys

# Read the corrected file from Windows
with open('c:\\Downloads\\mushroom\\modbus_sensor.py', 'r') as f:
    content = f.read()

# Write it directly to pi via scp-like approach using Python  
# First, let's just fix the broken file on the pie directly
with open('/home/mushroom/mushroom_project/modbus_sensor.py', 'w') as f:
    f.write(content)
    
print("File copied successfully")

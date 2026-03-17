#!/usr/bin/env python3
import paramiko
import sys

host = '192.168.10.2'
username = 'mushroom'
password = 'Mushroom@2024'

try:
    # Connect via SSH
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password, timeout=10)
    print(f"✅ Connected to {host}")
    
    # Fix the file by removing bad lines
    cmd = "sed -i '85,87d' ~/mushroom_project/modbus_sensor.py && echo 'File fixed'"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode()
    print(f"✅ {result.strip()}")
    
    # Start Flask app
    cmd = "cd ~/mushroom_project && source venv/bin/activate && nohup python3 app.py > app.log 2>&1 &"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    print("✅ Flask app started in background")
    
    # Check if it's running
    import time
    time.sleep(2)
    cmd = "curl -s http://localhost:5000/api/sensors | head -50"
    stdin, stdout, stderr = ssh.exec_command(cmd)
    result = stdout.read().decode()
    if result:
        print(f"✅ Dashboard API responding:\n{result[:200]}")
    else:
        print("⏳ Dashboard starting, try http://raspberrypi.local:5000 in a moment")
    
    ssh.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    sys.exit(1)

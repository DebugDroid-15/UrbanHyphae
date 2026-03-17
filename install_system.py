#!/usr/bin/env python3
"""Install Flask system-wide and run app"""
import paramiko
import time

host = 'raspberrypi.local'
username = 'mushroom'
password = 'Mushroom@2024'

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password, timeout=10)
    print("✅ Connected to Pi")
    
    # Install Flask system-wide as mushroom user
    print("⏳ Installing Flask system-wide...")
    stdin, stdout, stderr = ssh.exec_command('python3 -m pip install --user Flask pymodbus 2>&1 | tail -5')
    time.sleep(10)
    output = stdout.read().decode()
    print(output)
    
    # Kill old processes
    ssh.exec_command('pkill -9 -f "python3 app.py"')
    time.sleep(1)
    
    # Start Flask with system Python
    print("⏳ Starting Flask...")
    ssh.exec_command('cd ~/mushroom_project && nohup python3 app.py > app.log 2>&1 &')
    time.sleep(3)
    
    # Check if it's running
    stdin, stdout, stderr = ssh.exec_command('curl -s -m 5 http://localhost:5000 | head -c 50')
    result = stdout.read().decode()
    
    if result:
        print(f"✅ DASHBOARD IS ONLINE!")
        print(f"   http://192.168.10.2:5000")
    else:
        # Check logs
        stdin, stdout, stderr = ssh.exec_command('tail -20 ~/mushroom_project/app.log')
        logs = stdout.read().decode()
        print("⏳ Dashboard may still be starting...")
        print(logs[-300:] if logs else "No logs")
    
    ssh.close()
    
except Exception as e:
    print(f"Error: {e}")

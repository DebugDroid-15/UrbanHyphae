#!/usr/bin/env python3
import paramiko
import time

SSH_HOST = "raspberrypi.local"
SSH_USER = "mushroom"
SSH_PASSWORD = "Mushroom@2024"

try:
    # Connect
    client = paramiko.SSHClient()
    client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    client.connect(SSH_HOST, username=SSH_USER, password=SSH_PASSWORD, timeout=30)
    print("✅ Connected to Pi")
    
    # Kill old processes
    client.exec_command("pkill -9 -f 'python3 app.py'")
    time.sleep(1)
    
    # Start Flask in background
    client.exec_command("cd ~/mushroom_project && nohup python3 app.py > app.log 2>&1 &")
    print("✅ Flask started")
    
    # Wait for startup
    time.sleep(3)
    
    # Check if it's running
    stdin, stdout, stderr = client.exec_command("curl -s http://localhost:5000 | head -c 50")
    response = stdout.read().decode()
    
    if response:
        print("✅ Dashboard responsive!")
        print(f"Response: {response[:50]}")
    else:
        logs = client.exec_command("tail -20 ~/mushroom_project/app.log")
        print("❌ Dashboard not responding. Logs:")
        print(logs[1].read().decode())
    
    client.close()
    
except Exception as e:
    print(f"❌ Error: {e}")

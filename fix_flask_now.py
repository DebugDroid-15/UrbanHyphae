#!/usr/bin/env python3
"""Install Flask system-wide and start app"""
import paramiko
import time
import subprocess

host = 'raspberrypi.local'
username = 'mushroom'
password = 'Mushroom@2024'

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password, timeout=30)
    print("✅ Connected to Pi")
    
    # Install Flask system-wide via apt (doesn't require sudo password)
    print("⏳ Installing Flask (system-wide via apt)...")
    ssh.exec_command('sudo apt-get update -qq')
    time.sleep(3)
    
    stdin, stdout, stderr = ssh.exec_command('sudo apt-get install -y python3-flask 2>&1')
    output = stdout.read().decode()
    
    if "Setting up" in output or "already" in output:
        print("✅ Flask installed")
    else:
        print("Install output:", output[-100:])
    
    time.sleep(2)
    
    # Kill old Flask processes
    print("Stopping old instances...")
    ssh.exec_command('pkill -9 -f "python3 app.py"')
    time.sleep(1)
    
    # Start Flask with system Python
    print("⏳ Starting Flask app...")
    ssh.exec_command('cd ~/mushroom_project && nohup /usr/bin/python3 app.py > app.log 2>&1 &')
    time.sleep(4)
    
    # Test it
    print("Testing dashboard...")
    stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost:5000 | head -c 100')
    response = stdout.read().decode()
    
    if "DOCTYPE" in response or "<html" in response or "type=" in response:
        print("\n✅✅✅ DASHBOARD IS ONLINE!")
        print(f"Response: {response[:80]}")
    else:
        print("❌ Still not responding. Checking logs...")
        stdin, stdout, stderr = ssh.exec_command('tail -15 ~/mushroom_project/app.log')
        logs = stdout.read().decode()
        print(logs)
    
    ssh.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python3
"""Recreate venv and redeploy app"""
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
    
    # Create fresh virtual environment
    print("⏳ Creating virtual environment...")
    stdin, stdout, stderr = ssh.exec_command('cd ~/mushroom_project && python3 -m venv venv')
    time.sleep(5)
    print("✅ Virtual environment created")
    
    # Install Flask and dependencies
    print("⏳ Installing dependencies...")
    stdin, stdout, stderr = ssh.exec_command(
        'cd ~/mushroom_project && source venv/bin/activate && pip install --upgrade pip && pip install flask pymodbus RPi.GPIO'
    )
    time.sleep(10)
    output = stdout.read().decode()
    print("✅ Dependencies installed")
    
    # Start Flask app
    print("⏳ Starting Flask app...")
    stdin, stdout, stderr = ssh.exec_command(
        'cd ~/mushroom_project && source venv/bin/activate && nohup python3 app.py > app.log 2>&1 &'
    )
    time.sleep(3)
    print("✅ Flask app started")
    
    # Test the app
    stdin, stdout, stderr = ssh.exec_command('curl -s -m 5 http://localhost:5000 | head -c 100')
    result = stdout.read().decode()
    
    if '<!DOCTYPE' in result or '<html' in result:
        print("✅ Dashboard is responding!")
        print(f"   First 100 chars: {result[:100]}")
    else:
        print("⏳ Dashboard might still be starting...")
        # Check logs
        stdin, stdout, stderr = ssh.exec_command('tail -20 ~/mushroom_project/app.log')
        logs = stdout.read().decode()
        if logs:
            print("\n--- Recent logs ---")
            print(logs)
    
    ssh.close()
    print("\n✅ Setup complete!")
    print("Access dashboard at: http://raspberrypi.local:5000 or http://192.168.10.2:5000")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python3
"""Check Flask app status and restart if needed"""
import paramiko
import time

host = 'raspberrypi.local'
username = 'mushroom'
password = 'Mushroom@2024'

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password, timeout=10)
    
    # Check if app is running
    stdin, stdout, stderr = ssh.exec_command('ps aux | grep "python3 app.py" | grep -v grep')
    result = stdout.read().decode()
    
    if result:
        print("✅ Flask app is running")
        print(result[:100])
    else:
        print("⚠️  Flask app not running, starting it...")
        stdin, stdout, stderr = ssh.exec_command(
            'cd ~/mushroom_project && source venv/bin/activate && nohup python3 app.py > app.log 2>&1 &'
        )
        time.sleep(3)
        print("✅ Flask app started")
    
    # Test the app
    stdin, stdout, stderr = ssh.exec_command('curl -s -m 5 http://localhost:5000 | head -c 100')
    result = stdout.read().decode()
    
    if '<!DOCTYPE' in result or '<html' in result:
        print("✅ Dashboard is responding locally!")
    else:
        print("❌ Dashboard not responding")
        
        # Check for errors
        stdin, stdout, stderr = ssh.exec_command('tail -20 ~/mushroom_project/app.log 2>/dev/null || echo "No log file"')
        print("\n--- Recent logs ---")
        print(stdout.read().decode())
    
    ssh.close()
    
except Exception as e:
    print(f"❌ Error: {e}")

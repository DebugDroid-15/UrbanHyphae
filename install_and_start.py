#!/usr/bin/env python3
"""Install dependencies and start Flask"""
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
    
    # Install Flask and dependencies
    print("⏳ Installing Flask...")
    stdin, stdout, stderr = ssh.exec_command(
        'cd ~/mushroom_project && source venv/bin/activate && pip install Flask -q'
    )
    time.sleep(5)
    print("✅ Flask installed")
    
    print("⏳ Installing Pymodbus...")
    stdin, stdout, stderr = ssh.exec_command(
        'cd ~/mushroom_project && source venv/bin/activate && pip install pymodbus -q'
    )
    time.sleep(5)
    print("✅ Pymodbus installed")
    
    print("⏳ Installing RPi.GPIO...")
    stdin, stdout, stderr = ssh.exec_command(
        'cd ~/mushroom_project && source venv/bin/activate && pip install RPi.GPIO -q'
    )
    time.sleep(3)
    print("✅ RPi.GPIO installed")
    
    # Kill any old processes
    ssh.exec_command('pkill -9 -f "python3 app.py"')
    time.sleep(1)
    
    # Start Flask
    print("⏳ Starting Flask app...")
    stdin, stdout, stderr = ssh.exec_command(
        'cd ~/mushroom_project && source venv/bin/activate && nohup python3 app.py > app.log 2>&1 &'
    )
    time.sleep(3)
    
    # Check if it started
    stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost:5000 | head -c 50')
    result = stdout.read().decode()
    
    if result:
        print(f"✅ DASHBOARD IS NOW ONLINE!")
        print(f"   Access at: http://192.168.10.2:5000")
    else:
        # Check logs
        stdin, stdout, stderr = ssh.exec_command('tail -10 ~/mushroom_project/app.log')
        logs = stdout.read().decode()
        print(f"❌ Still not responding")
        print(f"\n--- Logs ---")
        print(logs)
    
    ssh.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python3
"""Install packages using full venv path"""
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
    
    # Use full path to pip
    venv_pip = '/home/mushroom/mushroom_project/venv/bin/pip'
    venv_python = '/home/mushroom/mushroom_project/venv/bin/python3'
    
    print("⏳ Installing Flask...")
    ssh.exec_command(f'{venv_pip} install -q Flask')
    time.sleep(5)
    
    print("⏳ Installing Pymodbus...")
    ssh.exec_command(f'{venv_pip} install -q pymodbus')
    time.sleep(5)
    
    print("⏳ Installing RPi.GPIO...")
    ssh.exec_command(f'{venv_pip} install -q RPi.GPIO')
    time.sleep(3)
    
    print("✅ All dependencies installed")
    
    # Kill old processes
    ssh.exec_command('pkill -9 -f "python3 app.py"')
    time.sleep(1)
    
    # Start Flask with full path
    print("⏳ Starting Flask app...")
    ssh.exec_command(f'cd ~/mushroom_project && nohup {venv_python} app.py > app.log 2>&1 &')
    time.sleep(3)
    
    # Check if it started
    stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost:5000 | head -c 50')
    result = stdout.read().decode()
    
    if result:
        print(f"✅ DASHBOARD IS ONLINE!")
        print(f"   Open: http://192.168.10.2:5000")
    else:
        # Check logs
        stdin, stdout, stderr = ssh.exec_command('tail -15 ~/mushroom_project/app.log')
        logs = stdout.read().decode()
        print(f"⏳ Checking status...")
        print(logs if logs else "No logs yet")
    
    ssh.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

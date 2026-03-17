#!/usr/bin/env python3
"""Copy modbus_sensor.py to Pi and start Flask app"""
import paramiko
import time

host = 'raspberrypi.local'
username = 'mushroom'
password = 'Mushroom@2024'

try:
    # Connect
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password, timeout=10)
    print("✅ Connected to Pi")
    
    # Copy file using SFTP
    sftp = ssh.open_sftp()
    sftp.put('c:\\Downloads\\mushroom\\modbus_sensor.py', 
             '/home/mushroom/mushroom_project/modbus_sensor.py')
    sftp.close()
    print("✅ File copied to Pi")
    
    # Start Flask app
    stdin, stdout, stderr = ssh.exec_command(
        'cd ~/mushroom_project && source venv/bin/activate && nohup python3 app.py > app.log 2>&1 &'
    )
    time.sleep(2)
    print("✅ Flask app started")
    
    # Check if it's running
    stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost:5000 | head -c 50')
    result = stdout.read().decode()
    if result:
        print(f"✅ Dashboard responding! First 50 chars: {result[:50]}")
    else:
        print("⏳ Dashboard starting up...")
    
    ssh.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

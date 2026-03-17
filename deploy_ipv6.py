#!/usr/bin/env python3
"""Deploy updated app.py and restart Flask"""
import paramiko
import time

host = 'raspberrypi.local'
username = 'mushroom'
password = 'Mushroom@2024'

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password, timeout=10)
    
    # Copy updated app.py
    sftp = ssh.open_sftp()
    sftp.put('c:\\Downloads\\mushroom\\app.py', 
             '/home/mushroom/mushroom_project/app.py')
    sftp.close()
    print("✅ Updated app.py copied to Pi")
    
    # Kill existing Flask process
    stdin, stdout, stderr = ssh.exec_command('pkill -f "python3 app.py"')
    time.sleep(1)
    
    # Start Flask app with IPv6 support
    stdin, stdout, stderr = ssh.exec_command(
        'cd ~/mushroom_project && source venv/bin/activate && nohup python3 app.py > app.log 2>&1 &'
    )
    time.sleep(2)
    print("✅ Flask app restarted with IPv6 support")
    
    # Test via IPv6 hostname
    stdin, stdout, stderr = ssh.exec_command('curl -s -m 5 http://localhost:5000 | head -c 50')
    result = stdout.read().decode()
    if result:
        print(f"✅ Dashboard responding: {result[:50]}")
    
    ssh.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

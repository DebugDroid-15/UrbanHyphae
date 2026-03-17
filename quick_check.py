#!/usr/bin/env python3
"""Quick diagnostic - check if Flask is running and restart if needed"""
import paramiko
import time

host = 'raspberrypi.local'
username = 'mushroom'
password = 'Mushroom@2024'

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password, timeout=10)
    
    # Kill any old Flask processes
    ssh.exec_command('pkill -9 -f "python3 app.py"')
    time.sleep(1)
    print("✅ Killed old processes")
    
    # Remove old log
    ssh.exec_command('rm -f ~/mushroom_project/app.log')
    
    # Start Flask fresh
    stdin, stdout, stderr = ssh.exec_command(
        'cd ~/mushroom_project && source venv/bin/activate && python3 app.py > app.log 2>&1 &'
    )
    time.sleep(3)
    print("✅ Flask app started in background")
    
    # Tail the log
    stdin, stdout, stderr = ssh.exec_command('tail -20 ~/mushroom_project/app.log')
    logs = stdout.read().decode()
    print("\n--- Flask Logs ---")
    print(logs if logs else "No logs yet")
    
    # Test locally from Pi
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost:5000 | head -c 50')
    result = stdout.read().decode()
    
    if result:
        print(f"\n✅ DASHBOARD IS RESPONDING!")
        print(f"   Content: {result[:50]}")
    else:
        print(f"\n❌ Dashboard not responding locally")
        # Check if Flask crashed
        stdin, stdout, stderr = ssh.exec_command('ps aux | grep "python3 app.py" | grep -v grep')
        ps = stdout.read().decode()
        if ps:
            print(f"   Process is running: {ps[:100]}")
        else:
            print(f"   Flask process crashed!")
    
    ssh.close()
    
except Exception as e:
    print(f"❌ Error: {e}")

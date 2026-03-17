#!/usr/bin/env python3
"""Clean and redeploy dashboard files to Pi"""
import paramiko
import os
import time

host = 'raspberrypi.local'
username = 'mushroom'
password = 'Mushroom@2024'

files_to_upload = [
    ('c:\\Downloads\\mushroom\\app.py', '/home/mushroom/mushroom_project/app.py'),
    ('c:\\Downloads\\mushroom\\modbus_sensor.py', '/home/mushroom/mushroom_project/modbus_sensor.py'),
    ('c:\\Downloads\\mushroom\\dashboard.html', '/home/mushroom/mushroom_project/dashboard.html'),
    ('c:\\Downloads\\mushroom\\calibration_config.py', '/home/mushroom/mushroom_project/calibration_config.py'),
]

try:
    # Connect
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password, timeout=10)
    print("✅ Connected to Pi")
    
    # Kill any running Flask process
    stdin, stdout, stderr = ssh.exec_command('pkill -f "python3 app.py"')
    time.sleep(1)
    print("✅ Stopped any running Flask processes")
    
    # Clean the project directory
    stdin, stdout, stderr = ssh.exec_command('rm -rf ~/mushroom_project/*')
    time.sleep(1)
    print("✅ Cleaned mushroom_project directory")
    
    # Upload files via SFTP
    sftp = ssh.open_sftp()
    
    for local_file, remote_file in files_to_upload:
        if os.path.exists(local_file):
            sftp.put(local_file, remote_file)
            print(f"✅ Uploaded {os.path.basename(local_file)}")
        else:
            print(f"⚠️  File not found: {local_file}")
    
    sftp.close()
    
    # Wait a moment
    time.sleep(1)
    
    # Start Flask app
    stdin, stdout, stderr = ssh.exec_command(
        'cd ~/mushroom_project && source venv/bin/activate && nohup python3 app.py > app.log 2>&1 &'
    )
    time.sleep(3)
    print("✅ Flask app started")
    
    # Verify it's running
    stdin, stdout, stderr = ssh.exec_command('curl -s http://localhost:5000 | head -c 50')
    result = stdout.read().decode()
    
    if result:
        print(f"✅ Dashboard online: {result[:50]}")
    else:
        print("⏳ Dashboard starting up...")
        # Check logs for errors
        stdin, stdout, stderr = ssh.exec_command('tail -10 ~/mushroom_project/app.log')
        logs = stdout.read().decode()
        if logs:
            print("\n--- Recent logs ---")
            print(logs)
    
    ssh.close()
    print("\n✅ Deployment complete!")
    print("Access dashboard at: http://raspberrypi.local:5000 or http://192.168.10.2:5000")
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

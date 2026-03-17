#!/usr/bin/env python3
"""
Complete clean deployment - delete everything, clear issues, and re-upload fresh
"""

import paramiko
import os
import time
from pathlib import Path

# Configuration
PI_HOST = 'raspberrypi.local'
PI_USER = 'mushroom'
PI_PASSWORD = 'Mushroom@2024'
PI_PROJECT_DIR = '/home/mushroom/mushroom_project'

# Local files to upload
LOCAL_FILES = {
    'app.py': r'c:\Downloads\mushroom\app.py',
    'modbus_sensor.py': r'c:\Downloads\mushroom\modbus_sensor.py',
    'dashboard.html': r'c:\Downloads\mushroom\dashboard.html',
    'calibration_config.py': r'c:\Downloads\mushroom\calibration_config.py',
}

def execute_command(ssh, command):
    """Execute SSH command and return output"""
    print(f"  ➜ {command}")
    stdin, stdout, stderr = ssh.exec_command(command)
    output = stdout.read().decode('utf-8', errors='ignore')
    error = stderr.read().decode('utf-8', errors='ignore')
    return output, error

def main():
    print("🔄 COMPLETE CLEAN DEPLOYMENT")
    print("=" * 60)
    
    # Connect to Pi
    print("\n1️⃣  Connecting to Pi...")
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    
    try:
        ssh.connect(PI_HOST, username=PI_USER, password=PI_PASSWORD, timeout=10)
        print("   ✅ Connected to", PI_HOST)
    except Exception as e:
        print(f"   ❌ Connection failed: {e}")
        return False
    
    # Kill any running Flask processes
    print("\n2️⃣  Stopping any running Flask processes...")
    execute_command(ssh, "pkill -9 -f 'python3 app.py' || true")
    time.sleep(1)
    print("   ✅ Processes stopped")
    
    # Completely delete project folder
    print(f"\n3️⃣  Deleting {PI_PROJECT_DIR} (complete cleanup)...")
    output, error = execute_command(ssh, f"rm -rf {PI_PROJECT_DIR}")
    time.sleep(1)
    print("   ✅ Project folder removed")
    
    # Create fresh project directory
    print(f"\n4️⃣  Creating fresh {PI_PROJECT_DIR}...")
    execute_command(ssh, f"mkdir -p {PI_PROJECT_DIR}")
    print("   ✅ Project folder created")
    
    # Upload all files
    print("\n5️⃣  Uploading project files...")
    sftp = ssh.open_sftp()
    
    for filename, local_path in LOCAL_FILES.items():
        if not os.path.exists(local_path):
            print(f"   ⚠️  Local file not found: {local_path}")
            continue
        
        file_size = os.path.getsize(local_path)
        remote_path = f"{PI_PROJECT_DIR}/{filename}"
        
        try:
            sftp.put(local_path, remote_path)
            print(f"   ✅ Uploaded {filename} ({file_size} bytes)")
        except Exception as e:
            print(f"   ❌ Failed to upload {filename}: {e}")
    
    sftp.close()
    
    # Ensure Flask is installed system-wide
    print("\n6️⃣  Ensuring Flask is installed...")
    execute_command(ssh, "sudo apt-get update -qq")
    output, error = execute_command(ssh, "sudo apt-get install -y python3-flask python3-pip 2>&1 | tail -5")
    print("   ✅ Flask dependencies ready")
    
    # Start Flask app in background
    print("\n7️⃣  Starting Flask app...")
    execute_command(ssh, f"cd {PI_PROJECT_DIR} && nohup python3 app.py > app.log 2>&1 &")
    time.sleep(3)
    print("   ✅ Flask app started")
    
    # Verify Flask is running
    print("\n8️⃣  Verifying Flask is responding...")
    output, error = execute_command(ssh, "curl -s http://localhost:5000 | head -c 100")
    
    if '<!DOCTYPE' in output or '<html' in output:
        print("   ✅ Dashboard is responding!")
    else:
        print("   ⚠️  Checking logs...")
        output, error = execute_command(ssh, f"tail -20 {PI_PROJECT_DIR}/app.log")
        print(output)
    
    ssh.close()
    
    print("\n" + "=" * 60)
    print("✅ CLEAN DEPLOYMENT COMPLETE")
    print("\n📊 Access Dashboard:")
    print("   • http://192.168.10.2:5000 (Direct IP)")
    print("   • http://raspberrypi.local:5000 (Hostname)")
    print("\n📁 Project Directory:")
    print(f"   {PI_PROJECT_DIR}")
    print("\n📋 Log File:")
    print(f"   {PI_PROJECT_DIR}/app.log")
    
    return True

if __name__ == "__main__":
    main()

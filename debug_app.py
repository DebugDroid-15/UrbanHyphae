#!/usr/bin/env python3
"""Check what's wrong with the Flask app"""
import paramiko
import time

host = 'raspberrypi.local'
username = 'mushroom'
password = 'Mushroom@2024'

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password, timeout=10)
    
    # Check if directory exists
    stdin, stdout, stderr = ssh.exec_command('ls -la ~/mushroom_project/')
    print("--- Directory contents ---")
    print(stdout.read().decode())
    
    # Check if Python works
    stdin, stdout, stderr = ssh.exec_command('cd ~/mushroom_project && python3 -c "import sys; print(sys.version)"')
    print("\n--- Python version ---")
    print(stdout.read().decode())
    
    # Try importing Flask
    stdin, stdout, stderr = ssh.exec_command('cd ~/mushroom_project && source venv/bin/activate && python3 -c "import flask; print(flask.__version__)"')
    print("\n--- Flask version ---")
    out = stdout.read().decode()
    err = stderr.read().decode()
    print(out if out else err)
    
    # Try running app directly to see errors
    print("\n--- Running app (checking for import errors) ---")
    stdin, stdout, stderr = ssh.exec_command('cd ~/mushroom_project && source venv/bin/activate && timeout 5 python3 app.py 2>&1')
    output = stdout.read().decode()
    error = stderr.read().decode()
    
    print(output[:500] if output else "No stdout")
    if error:
        print(f"\nErrors: {error[:500]}")
    
    ssh.close()
    
except Exception as e:
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()

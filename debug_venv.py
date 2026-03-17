#!/usr/bin/env python3
"""Debug venv and install"""
import paramiko

host = 'raspberrypi.local'
username = 'mushroom'
password = 'Mushroom@2024'

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(host, username=username, password=password, timeout=10)
    
    # Check venv exists
    stdin, stdout, stderr = ssh.exec_command('ls -la ~/mushroom_project/venv/bin/ | head -20')
    print("--- venv/bin contents ---")
    print(stdout.read().decode())
    
    # Test pip directly
    print("\n--- Testing pip ---")
    stdin, stdout, stderr = ssh.exec_command('/home/mushroom/mushroom_project/venv/bin/pip --version')
    out = stdout.read().decode()
    err = stderr.read().decode()
    print(out if out else err)
    
    # Try installing Flask with full output
    print("\n--- Installing Flask ---")
    stdin, stdout, stderr = ssh.exec_command('/home/mushroom/mushroom_project/venv/bin/pip install Flask')
    out = stdout.read().decode()
    err = stderr.read().decode()
    print(out[-500:] if out else "")
    if err:
        print(f"Errors: {err[-500:]}")
    
    # Check if Flask is installed
    print("\n--- Checking Flask ---")
    stdin, stdout, stderr = ssh.exec_command('/home/mushroom/mushroom_project/venv/bin/python3 -c "import flask; print(flask.__version__)"')
    out = stdout.read().decode()
    err = stderr.read().decode()
    print(f"Flask version: {out if out else err}")
    
    ssh.close()
    
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

#!/usr/bin/env python3
import paramiko
import time

HOST = "raspberrypi.local"
USERNAME = "mushroom"
PASSWORD = "Mushroom@2024"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)

print("Creating install script on Pi...")

# Create install script
install_script = """#!/bin/bash
set -e
echo "Updating package list..."
sudo apt-get update -qq
echo "Installing Flask and dependencies..."
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3-flask python3-pymodbus
echo "Installation complete"
python3 -c "import flask; print('Flask version:', flask.__version__)"
"""

sftp = ssh.open_sftp()
with sftp.file("/home/mushroom/install_flask.sh", "w") as f:
    f.write(install_script)
sftp.close()

print("Running install script...")
stdin, stdout, stderr = ssh.exec_command("bash /home/mushroom/install_flask.sh", get_pty=True)
stdin.write("Mushroom@2024\n")
stdin.flush()
time.sleep(120)  # Wait for installation

# Check if it worked
print("\nChecking Flask...")
stdin, stdout, stderr = ssh.exec_command("python3 -c \"import flask; print('Flask installed:', flask.__version__)\"")
version = stdout.read().decode()
err = stderr.read().decode()
print(version if version else f"Error: {err}")

# Kill old Flask and start new
print("\nStarting Flask app...")
ssh.exec_command("pkill -9 -f 'python3 app.py'")
time.sleep(1)
ssh.exec_command("cd /home/mushroom/mushroom_monitoring && nohup python3 app.py > app.log 2>&1 &")
time.sleep(5)

# Test
print("Testing dashboard...")
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:5000 | head -c 100")
response = stdout.read().decode()

if "DOCTYPE" in response or "<html" in response:
    print("\n✅✅✅ DASHBOARD ONLINE!")
    print("Access: http://192.168.1.100:5000")
else:
    stdin, stdout, stderr = ssh.exec_command("tail -5 /home/mushroom/mushroom_monitoring/app.log")
    logs = stdout.read().decode()
    print("Logs:", logs)

ssh.close()

#!/usr/bin/env python3
import paramiko
import time

HOST = "raspberrypi.local"
USERNAME = "mushroom"
PASSWORD = "Mushroom@2024"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)

print("=" * 60)
print("INSTALLING FLASK SYSTEM-WIDE & STARTING DASHBOARD")
print("=" * 60)

# Kill old Flask
print("\nStopping old Flask instances...")
ssh.exec_command("pkill -9 -f 'python3 app.py'")
time.sleep(1)

# Install Flask system-wide via apt
print("Installing Flask system-wide...")
stdin, stdout, stderr = ssh.exec_command("sudo DEBIAN_FRONTEND=noninteractive apt-get install -y python3-flask python3-pymodbus 2>&1")
time.sleep(90)  # Give apt time to install
output = stdout.read().decode()
print("Installation finished")

time.sleep(3)

# Verify installation
print("\nVerifying Flask installation...")
stdin, stdout, stderr = ssh.exec_command("python3 -c 'import flask; print(\"Flask\", flask.__version__)'")
version = stdout.read().decode().strip()
print(f"System Flask: {version}")

# Start Flask with system Python (not venv)
print("\nStarting Flask app...")
ssh.exec_command("cd /home/mushroom/mushroom_monitoring && nohup python3 app.py > app.log 2>&1 &")
time.sleep(5)

# Test it
print("Testing dashboard endpoint...")
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:5000 | head -c 200")
response = stdout.read().decode()

if "DOCTYPE" in response or "<html" in response or "type=" in response:
    print("\n" + "=" * 60)
    print("✅✅✅ SUCCESS - DASHBOARD IS ONLINE!")
    print("=" * 60)
    print("\nAccess your dashboard at:")
    print("  👉 http://192.168.1.100:5000")
    print("\nYou can open this URL in your browser now!")
    print("=" * 60)
else:
    print("Still starting... checking logs:")
    time.sleep(3)
    stdin, stdout, stderr = ssh.exec_command("tail -10 /home/mushroom/mushroom_monitoring/app.log")
    logs = stdout.read().decode()
    print(logs)

ssh.close()

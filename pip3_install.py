#!/usr/bin/env python3
import paramiko
import time

HOST = "raspberrypi.local"
USERNAME = "mushroom"
PASSWORD = "Mushroom@2024"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)

print("Attempting Flask installation via pip3...")

# First check internet
print("\n1. Checking internet connectivity...")
stdin, stdout, stderr = ssh.exec_command("ping -c 1 8.8.8.8")
output = stdout.read().decode()
if "1 received" in output or "100%" in output:
    print("   ✅ Internet is reachable")
else:
    print("   ⚠️  Internet may be unreachable")

# Install via pip3 directly
print("\n2. Installing Flask with pip3...")
cmd = "pip3 install --upgrade pip setuptools && pip3 install Flask pymodbus"
stdin, stdout, stderr = ssh.exec_command(cmd)
time.sleep(60)
output = stdout.read().decode()
err = stderr.read().decode()

if "Successfully installed" in output or "Requirement already satisfied" in output:
    print("   ✅ Flask installed")
else:
    print(f"   Output: {output[-200:]}")
    if err:
        print(f"   Error: {err[-200:]}")

# Verify
print("\n3. Verifying Flask...")
stdin, stdout, stderr = ssh.exec_command("python3 -c 'import flask; print(\"Flask\", flask.__version__)'")
version = stdout.read().decode().strip()
if version:
    print(f"   ✅ {version}")
else:
    err = stderr.read().decode()
    print(f"   ❌ {err}")

# Start Flask
print("\n4. Starting Flask app...")
ssh.exec_command("pkill -9 -f 'python3 app.py'")
time.sleep(1)
ssh.exec_command("cd /home/mushroom/mushroom_monitoring && nohup python3 app.py > app.log 2>&1 &")
time.sleep(5)

# Test
print("\n5. Testing dashboard...")
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:5000 | head -c 100")
response = stdout.read().decode()

if "DOCTYPE" in response or "<html" in response:
    print("   ✅✅✅ DASHBOARD ONLINE!")
    print("\nAccess at: http://192.168.1.100:5000")
else:
    print("   Checking logs...")
    stdin, stdout, stderr = ssh.exec_command("tail -5 /home/mushroom/mushroom_monitoring/app.log")
    logs = stdout.read().decode()
    print(f"   {logs}")

ssh.close()

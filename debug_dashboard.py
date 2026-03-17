#!/usr/bin/env python3
import paramiko
import time

HOST = "raspberrypi.local"
USERNAME = "mushroom"
PASSWORD = "Mushroom@2024"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)

print("DIAGNOSING DASHBOARD ISSUE")
print("=" * 60)

# Check if dummy_dashboard.html exists
print("\n1. Checking if dummy_dashboard.html exists...")
stdin, stdout, stderr = ssh.exec_command("ls -la /home/mushroom/mushroom_monitoring/dummy_dashboard.html")
result = stdout.read().decode().strip()
if result and "No such file" not in result:
    print(f"   ✅ File exists: {result[:60]}")
else:
    print("   ❌ File NOT found!")

# Check if server is running
print("\n2. Checking if server is running...")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep minimal_server | grep -v grep")
procs = stdout.read().decode()
if procs:
    print("   ✅ Server running")
    print(procs[:100])
else:
    print("   ❌ Server NOT running - starting...")
    ssh.exec_command("cd /home/mushroom/mushroom_monitoring && python3 minimal_server.py > minimal_server.log 2>&1 &")
    time.sleep(3)

# Test locally
print("\n3. Testing locally on Pi...")
stdin, stdout, stderr = ssh.exec_command("curl -v http://localhost:5000 2>&1 | head -20")
result = stdout.read().decode()
print(result)

# Check server logs
print("\n4. Checking server logs...")
stdin, stdout, stderr = ssh.exec_command("tail -20 /home/mushroom/mushroom_monitoring/minimal_server.log")
logs = stdout.read().decode()
if logs:
    print(logs)
else:
    print("   (no logs yet)")

# Try manual GET
print("\n5. Testing dashboard file directly...")
stdin, stdout, stderr = ssh.exec_command("head -5 /home/mushroom/mushroom_monitoring/dummy_dashboard.html")
content = stdout.read().decode()
if "DOCTYPE" in content or "html" in content:
    print("   ✅ File is valid HTML")
else:
    print("   ❌ File may be corrupted")

ssh.close()

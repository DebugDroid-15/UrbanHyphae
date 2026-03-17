#!/usr/bin/env python3
import paramiko
import time

HOST = "raspberrypi.local"
USERNAME = "mushroom"
PASSWORD = "Mushroom@2024"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)

print("FRESH START - KILLING ALL PYTHON PROCESSES")
print("=" * 60)

#Kill ALL Python processes
print("\n1. Killing all Python processes...")
ssh.exec_command("killall -9 python3 2>/dev/null || true")
time.sleep(3)

# Verify all killed
stdin, stdout, stderr = ssh.exec_command("ps aux | grep python3 | grep -v grep")
result = stdout.read().decode()
if not result:
    print("   ✅ All Python processes killed")
else:
    print("   Still running:", result[:80])

# Wait for port to be released
print("\n2. Waiting for port 5000 to be released...")
for i in range(10):
    stdin, stdout, stderr = ssh.exec_command("lsof -i :5000 2>/dev/null || netstat -tln 2>/dev/null | grep 5000 || true")
    result = stdout.read().decode()
    if not result or "5000" not in result:
        print(f"   ✅ Port is free")
        break
    print(f"   Still waiting... ({i}s)")
    time.sleep(1)

# Start fresh server
print("\n3. Starting dashboard server...")
ssh.exec_command("cd /home/mushroom/mushroom_monitoring && python3 minimal_server.py > server.log 2>&1 &")
time.sleep(4)

# Test
print("\n4. Testing dashboard...")
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:5000 2>&1 | head -c 50")
response = stdout.read().decode()
print(f"   Response: {response[:50]}")

# Get IPs
stdin, stdout, stderr = ssh.exec_command("hostname -I")
ips = stdout.read().decode().strip().split()

print("\n" + "=" * 60)
if response:
    print("✅ DASHBOARD SERVER RUNNING!")
else:
    print("⚠️  Server may still be starting")

print("\nAccess at:")
for ip in ips:
    print(f"  👉 http://{ip}:5000")
print("=" * 60)

ssh.close()

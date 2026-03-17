#!/usr/bin/env python3
import paramiko
import time

HOST = "raspberrypi.local"  
USERNAME = "mushroom"
PASSWORD = "Mushroom@2024"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)

print("CHECKING CURRENT STATUS")
print("=" * 60)

# Find current IPs
print("\n1. Current IP addresses:")
stdin, stdout, stderr = ssh.exec_command("ip addr show | grep 'inet ' | grep -v '127.0.0.1'")
ips = stdout.read().decode()
for line in ips.strip().split('\n'):
    if line:
        print(f"   {line.strip()}")

# Check if server is running
print("\n2. Checking if dashboard server is running...")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep minimal_server | grep -v grep")
procs = stdout.read().decode()
if procs:
    print("   ✅ Server is running")
else:
    print("   ❌ Server NOT running - restarting...")
    ssh.exec_command("pkill -9 -f minimal_server")
    time.sleep(1)
    ssh.exec_command("cd /home/mushroom/mushroom_monitoring && nohup python3 minimal_server.py > minimal_server.log 2>&1 &")
    time.sleep(3)
    print("   ✅ Server restarted")

# Test locally first
print("\n3. Testing connection locally on Pi...")
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:5000 | head -c 50")
response = stdout.read().decode()
if response:
    print(f"   ✅ Local response: {response[:40]}")
else:
    print("   ❌ No local response")

# Get the actual IPs to try
print("\n4. Extracting IP addresses...")
stdin, stdout, stderr = ssh.exec_command("hostname -I")
ips_raw = stdout.read().decode().strip().split()
print(f"   IPs on Pi: {ips_raw}")

print("\n" + "=" * 60)
print("TRY THESE URLS:")
for ip in ips_raw:
    print(f"  👉 http://{ip}:5000")
print("=" * 60)

ssh.close()

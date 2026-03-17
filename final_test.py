#!/usr/bin/env python3
import paramiko
import time

HOST = "raspberrypi.local"
USERNAME = "mushroom"
PASSWORD = "Mushroom@2024"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)

print("FINAL TEST - DASHBOARD ACCESS")
print("=" * 60)

# Wait a moment for server to fully start
time.sleep(2)

# Get IPs
stdin, stdout, stderr = ssh.exec_command("hostname -I")
ips = stdout.read().decode().strip().split()

print("\nTesting each IP:\n")

working_ips = []
for ip in ips:
    stdin, stdout, stderr = ssh.exec_command(f"curl -s -m 3 http://{ip}:5000 | head -c 50")
    response = stdout.read().decode()
    
    if "DOCTYPE" in response or "<html" in response or "html" in response.lower():
        print(f"  ✅ http://{ip}:5000 - WORKING!")
        working_ips.append(ip)
    else:
        print(f"  ❌ http://{ip}:5000 - Not responding")

if working_ips:
    print("\n" + "=" * 60)
    print("✅✅✅ DASHBOARD IS LIVE!")
    print("=" * 60)
    print("\nYou can access the dashboard at:\n")
    for ip in working_ips:
        print(f"  👉 http://{ip}:5000")
    print("\nOpen one of these URLs in your browser now!")
else:
    print("\n❌ No IPs responding. Checking logs...")
    stdin, stdout, stderr = ssh.exec_command("tail -10 /home/mushroom/mushroom_monitoring/server.log")
    logs = stdout.read().decode()
    print(logs)

print("=" * 60)
ssh.close()

#!/usr/bin/env python3
import paramiko
import time

HOST = "raspberrypi.local"
USERNAME = "mushroom"
PASSWORD = "Mushroom@2024"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)

# Check if Flask is running
print("Checking Flask status...\n")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep -i python | grep -v grep")
output = stdout.read().decode()
print("Running processes:")
print(output if output else "  (none)")

# Check logs
print("\nApp logs (last 20 lines):")
stdin, stdout, stderr = ssh.exec_command("tail -20 /home/mushroom/mushroom_monitoring/app.log")
logs = stdout.read().decode()
print(logs if logs else "  (no logs)")

# Test dashboard
print("\nTesting dashboard endpoint...")
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:5000 | head -c 100")
response = stdout.read().decode()
print(f"Response: {response if response else '(no response)'}")

# Check project files
print("\nProject files:")
stdin, stdout, stderr = ssh.exec_command("ls -la /home/mushroom/mushroom_monitoring/")
files = stdout.read().decode()
print(files)

ssh.close()

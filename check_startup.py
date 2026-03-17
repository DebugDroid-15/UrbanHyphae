#!/usr/bin/env python3
import paramiko
import time

HOST = "raspberrypi.local"
USERNAME = "mushroom"
PASSWORD = "Mushroom@2024"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)

print("CHECKING SERVER STARTUP")
print("=" * 60)

# Check server log
print("\n1. Server log:")
stdin, stdout, stderr = ssh.exec_command("tail -30 /home/mushroom/mushroom_monitoring/server.log")
logs = stdout.read().decode()
print(logs if logs else "   (empty)")

# Check if process is running
print("\n2. Checking if process started...")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep minimal_server | grep -v grep")
procs = stdout.read().decode()
if procs:
    print("   ✅ Process running")
    print(procs[:100])
else:
    print("   ❌ Process not running")
    
    print("\n3. Trying to start manually...")
    # Start with explicit Python path
    ssh.exec_command("cd /home/mushroom/mushroom_monitoring && /usr/bin/python3 minimal_server.py > server.log 2>&1 &")
    time.sleep(4)
    
    # Check again
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep python3 | grep minimal")
    procs = stdout.read().decode()
    if procs:
        print("   ✅ Started successfully")
    else:
        print("   Still not running")

# Test conn
print("\n4. Quick test...")
stdin, stdout, stderr = ssh.exec_command("curl -m 3 http://localhost:5000 2>&1 | head -c 50")
response = stdout.read().decode()
if response:
    print(f"   ✅ Response: {response[:50]}")
else:
    print("   ❌ No response")
    
    # Check if port is even open
    stdin, stdout, stderr = ssh.exec_command("netstat -tln | grep 5000 || ss -tln | grep 5000")
    port_check = stdout.read().decode()
    print(f"   Port check: {port_check[:100] if port_check else 'Port not listening'}")

ssh.close()

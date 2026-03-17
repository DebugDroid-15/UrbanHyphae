#!/usr/bin/env python3
import paramiko
import time

HOST = "raspberrypi.local"
USERNAME = "mushroom"
PASSWORD = "Mushroom@2024"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)

print("CHECKING PORT 5000")
print("=" * 60)

# Check what's listening on port 5000
print("\n1. What's listening on port 5000?")
stdin, stdout, stderr = ssh.exec_command("netstat -tlnp 2>/dev/null | grep 5000 || ss -tlnp 2>/dev/null | grep 5000")
result = stdout.read().decode()
if result:
    print(result.strip())
else:
    print("   No process found on port 5000")

# Kill and restart fresh
print("\n2. Killing and restarting server...")
ssh.exec_command("pkill -9 -f minimal_server")
ssh.exec_command("pkill -9 -f 'python3' 2>/dev/null || true")
time.sleep(2)

# Start in foreground first to see any errors
print("\n3. Starting server and checking for errors...")
stdin, stdout, stderr = ssh.exec_command("cd /home/mushroom/mushroom_monitoring && timeout 5 python3 minimal_server.py")
time.sleep(6)
output = stdout.read().decode()
errors = stderr.read().decode()

print("Output:", output if output else "(none)")
if errors:
    print("Errors:", errors)

# Now start in background
print("\n4. Starting server in background...")
ssh.exec_command("cd /home/mushroom/mushroom_monitoring && nohup python3 minimal_server.py > server.log 2>&1 &")
time.sleep(3)

# Check processes
print("\n5. Process status...")
stdin, stdout, stderr = ssh.exec_command("ps aux | grep python3 | grep -v grep")
procs = stdout.read().decode()
for line in procs.split('\n'):
    if line.strip():
        print(f"   {line[:120]}")

# Test again
print("\n6. Testing on all IPs...")
stdin, stdout, stderr = ssh.exec_command("hostname -I")
ips = stdout.read().decode().strip().split()

for ip in ips:
    stdin, stdout, stderr = ssh.exec_command(f"curl -s -m 2 http://{ip}:5000 | head -c 30")
    response = stdout.read().decode()
    status = "✅" if response else "❌"
    print(f"   {status} http://{ip}:5000 - {response[:25]}")

ssh.close()

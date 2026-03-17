#!/usr/bin/env python3
import paramiko
import time

HOST = "raspberrypi.local"
USERNAME = "mushroom"
PASSWORD = "Mushroom@2024"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)

print("Checking and fixing network configuration...")
print("=" * 60)

# Check current DNS
print("\n1. Checking current DNS...")
stdin, stdout, stderr = ssh.exec_command("cat /etc/resolv.conf")
dns_config = stdout.read().decode()
print(dns_config[:200])

# Set DNS to Google
print("\n2. Configuring DNS...")
ssh.exec_command("echo 'nameserver 8.8.8.8' | sudo tee /etc/resolv.conf > /dev/null")
ssh.exec_command("echo 'nameserver 8.8.4.4' | sudo tee -a /etc/resolv.conf > /dev/null")
print("   ✅ DNS updated")

# Test connectivity
print("\n3. Testing internet...")
stdin, stdout, stderr = ssh.exec_command("ping -c 1 8.8.8.8")
output = stdout.read().decode()
if "1 received" in output:
    print("   ✅ Internet connection OK")
else:
    print("   ❌ Still no internet")
    print("   You may need to check Pi network settings")

# Try apt update
print("\n4. Testing apt...")
stdin, stdout, stderr = ssh.exec_command("sudo apt-get update -qq 2>&1 | head -5")
time.sleep(10)
out = stdout.read().decode()[:100]
print(f"   Output: {out}")

# Install pip3 and Flask
print("\n5. Installing dependencies...")
ssh.exec_command("sudo apt-get install -y python3-pip 2>&1 &")
time.sleep(90)

ssh.exec_command("pip3 install Flask pymodbus 2>&1 &")
time.sleep(90)

# Start Flask
print("\n6. Starting Flask...")
ssh.exec_command("pkill -9 -f 'python3 app.py'")
time.sleep(1)
ssh.exec_command("cd /home/mushroom/mushroom_monitoring && nohup python3 app.py > app.log 2>&1 &")
time.sleep(5)

# Test
print("\n7. Testing dashboard...")
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:5000 | head -c 50")
response = stdout.read().decode()

if response:
    print("   ✅ Response received!")
    if "DOCTYPE" in response or "<html" in response:
        print("\n" + "=" * 60)
        print("✅✅✅ DASHBOARD ONLINE!")
        print("=" * 60)
        print("\nAccess at: http://192.168.1.100:5000")
    else:
        print("   Response:", response[:50])
else:
    print("   Still starting, check logs in a moment...")
    stdin, stdout, stderr = ssh.exec_command("tail -3 /home/mushroom/mushroom_monitoring/app.log")
    logs = stdout.read().decode()
    print(logs)

ssh.close()

#!/usr/bin/env python3
import paramiko
import time

HOST = "raspberrypi.local"
USERNAME = "mushroom"
PASSWORD = "Mushroom@2024"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)

print("COMPLETE SETUP WITH PROPER DEPENDENCY INSTALLATION")
print("=" * 60)

# Step 1: Install python3-pip
print("\n1. Installing Python3 and pip...")
stdin, stdout, stderr = ssh.exec_command("sudo apt-get update && sudo apt-get install -y python3-pip", timeout=None)
time.sleep(120)  # Long timeout for apt

# Step 2: Install Flask via pip3
print("2. Installing Flask...")
stdin, stdout, stderr = ssh.exec_command("pip3 install Flask pymodbus")
time.sleep(60)

stdin, stdout, stderr = ssh.exec_command("python3 -c 'import flask; print(\"Flask\", flask.__version__)'")
version = stdout.read().decode().strip()
if version:
    print(f"   ✅ {version}")
else:
    print("   Still installing...")
    time.sleep(30)
    stdin, stdout, stderr = ssh.exec_command("python3 -c 'import flask; print(\"Flask\", flask.__version__)'")
    version = stdout.read().decode().strip()
    print(f"   {version if version else 'Not ready yet'}")

# Step 3: Start Flask
print("\n3. Starting Flask app...")
ssh.exec_command("pkill -9 -f 'python3 app.py'")
time.sleep(1)
ssh.exec_command("cd /home/mushroom/mushroom_monitoring && nohup python3 app.py > app.log 2>&1 &")
time.sleep(5)

# Step 4: Test
print("\n4. Testing dashboard...")
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:5000 | head -c 100")
response = stdout.read().decode()

if "DOCTYPE" in response or "<html" in response:
    print("   ✅✅✅ SUCCESS!")
    print("\n" + "=" * 60)
    print("DASHBOARD ONLINE")
    print("=" * 60)
    print("\nAccess your dashboard:")
    print("  👉 http://192.168.1.100:5000")
    print("=" * 60)
else:
    print("   Checking logs...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command("tail -8 /home/mushroom/mushroom_monitoring/app.log")
    logs = stdout.read().decode()
    print(logs)

ssh.close()

#!/usr/bin/env python3
import paramiko
import time

HOST = "raspberrypi.local"
USERNAME = "mushroom"
PASSWORD = "Mushroom@2024"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)

print("=" * 60)
print("DEPLOYING MINIMAL DASHBOARD SERVER")
print("(No Flask dependency required)")
print("=" * 60)

# Upload minimal server
print("\n1. Uploading minimal dashboard server...")
sftp = ssh.open_sftp()
sftp.put(r"c:\Downloads\mushroom\minimal_dashboard.py", "/home/mushroom/mushroom_monitoring/minimal_server.py")
sftp.close()
print("   ✅ Uploaded")

# Kill old processes
print("\n2. Stopping any running Flask...")
ssh.exec_command("pkill -9 -f 'python3 app.py'")
ssh.exec_command("pkill -9 -f 'minimal_server'")
time.sleep(1)

# Start minimal server
print("\n3. Starting minimal dashboard server...")
ssh.exec_command("cd /home/mushroom/mushroom_monitoring && nohup python3 minimal_server.py > minimal_server.log 2>&1 &")
time.sleep(3)

# Test
print("\n4. Testing dashboard...")
for attempt in range(5):
    stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:5000 | head -c 100")
    response = stdout.read().decode()
    
    if "DOCTYPE" in response or "<!DOCTYPE" in response or "<html" in response:
        print("\n" + "=" * 60)
        print("✅✅✅ DASHBOARD IS ONLINE!")
        print("=" * 60)
        print("\nAccess your substrate monitoring dashboard:")
        print("  👉 http://192.168.1.100:5000")
        print("\nThe dashboard is now running!")
        print("=" * 60)
        break
    else:
        print(f"   Attempt {attempt+1}: Starting up...")
        time.sleep(2)
else:
    print("\nChecking logs...")
    stdin, stdout, stderr = ssh.exec_command("tail -5 /home/mushroom/mushroom_monitoring/minimal_server.log")
    logs = stdout.read().decode()
    print(logs)

ssh.close()

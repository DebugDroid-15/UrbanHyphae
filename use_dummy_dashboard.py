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
print("SWITCHING TO DUMMY DASHBOARD")
print("=" * 60)

# Upload dummy dashboard
print("\n1. Uploading dummy_dashboard.html...")
sftp = ssh.open_sftp()
sftp.put(r"c:\Downloads\mushroom\dummy_dashboard.html", "/home/mushroom/mushroom_monitoring/dummy_dashboard.html")
print("   ✅ Uploaded")

# Upload updated minimal server
print("\n2. Uploading updated server...")
sftp.put(r"c:\Downloads\mushroom\minimal_dashboard.py", "/home/mushroom/mushroom_monitoring/minimal_server.py")
sftp.close()
print("   ✅ Uploaded")

# Restart server
print("\n3. Restarting dashboard server...")
ssh.exec_command("pkill -9 -f minimal_server")
time.sleep(2)
ssh.exec_command("cd /home/mushroom/mushroom_monitoring && nohup python3 minimal_server.py > minimal_server.log 2>&1 &")
time.sleep(3)

# Test
print("\n4. Testing dashboard...")
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:5000 | head -c 100")
response = stdout.read().decode()

if "DOCTYPE" in response or "<html" in response:
    print("   ✅ Dashboard responding!")
    
    # Get IPs
    stdin, stdout, stderr = ssh.exec_command("hostname -I")
    ips = stdout.read().decode().strip().split()
    
    print("\n" + "=" * 60)
    print("✅ DUMMY DASHBOARD IS NOW LIVE!")
    print("=" * 60)
    print("\nAccess at:")
    for ip in ips:
        print(f"  👉 http://{ip}:5000")
    print("=" * 60)
else:
    print("   Checking logs...")
    stdin, stdout, stderr = ssh.exec_command("tail -5 /home/mushroom/mushroom_monitoring/minimal_server.log")
    logs = stdout.read().decode()
    print(logs)

ssh.close()

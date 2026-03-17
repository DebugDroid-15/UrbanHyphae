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
print("FINAL SETUP VERIFICATION")
print("=" * 60)

# Check Flask installation
print("\n1. Checking Flask installation...")
stdin, stdout, stderr = ssh.exec_command("source /home/mushroom/mushroom_monitoring/venv/bin/activate && python3 -c 'import flask; print(flask.__version__)'")
version = stdout.read().decode().strip()
err = stderr.read().decode()

if version and "error" not in err.lower():
    print(f"   ✅ Flask {version} installed")
else:
    print("   ⚠️  Flask not found - installing from system...")
    ssh.exec_command("sudo apt-get install -y python3-flask")
    time.sleep(5)

# Kill old Flask
print("\n2. Starting Flask app...")
ssh.exec_command("pkill -9 -f 'python3 app.py'")
time.sleep(1)

ssh.exec_command("cd /home/mushroom/mushroom_monitoring && source venv/bin/activate && nohup python3 app.py > app.log 2>&1 &")
time.sleep(5)

# Test dashboard
print("\n3. Testing dashboard...")
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:5000 | head -c 150")
response = stdout.read().decode()

if "DOCTYPE" in response or "<html" in response:
    print("   ✅✅✅ DASHBOARD ONLINE!")
    print(f"\n   Access at: http://192.168.1.100:5000")
else:
    print("   Checking logs...")
    stdin, stdout, stderr = ssh.exec_command("tail -8 /home/mushroom/mushroom_monitoring/app.log")
    logs = stdout.read().decode()
    if logs:
        print("   Logs:")
        for line in logs.split('\n')[-8:]:
            if line.strip():
                print(f"   {line}")
    else:
        print("   (no logs yet - app may still be starting)")

print("\n" + "=" * 60)
ssh.close()

#!/usr/bin/env python3
import paramiko
import time

HOST = "raspberrypi.local"
USERNAME = "mushroom"
PASSWORD = "Mushroom@2024"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)

print("Waiting for package installs to finish...")
# Wait for apt processes to finish
for i in range(60):
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep apt | grep -v grep")
    procs = stdout.read().decode().strip()
    if not procs:
        print("✅ Package installs completed")
        break
    print(f"  Still installing... ({i}s)")
    time.sleep(1)

time.sleep(2)

# Kill any running Flask
print("Stopping old Flask instances...")
ssh.exec_command("pkill -9 -f 'python3 app.py'")
time.sleep(1)

# Start Flask from virtualenv
print("Starting Flask app from virtual environment...")
ssh.exec_command("cd /home/mushroom/mushroom_monitoring && source venv/bin/activate && nohup python3 app.py > app.log 2>&1 &")
time.sleep(4)

# Test it
print("Testing dashboard...")
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:5000 | head -c 100")
response = stdout.read().decode()

if "DOCTYPE" in response or "<html" in response or "type=" in response:
    print("✅✅✅ DASHBOARD ONLINE!")
    print(f"\nAccess at: http://192.168.1.100:5000")
else:
    print("Checking logs...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command("tail -15 /home/mushroom/mushroom_monitoring/app.log")
    logs = stdout.read().decode()
    print("App logs:")
    print(logs if logs else "(empty - app may still be starting)")
    
    # Also check Flask import
    print("\nTesting Flask import...")
    stdin, stdout, stderr = ssh.exec_command("python3 -c 'import flask; print(\"Flask version:\", flask.__version__)'")
    out = stdout.read().decode()
    err = stderr.read().decode()
    print(out if out else f"Error: {err}")

ssh.close()

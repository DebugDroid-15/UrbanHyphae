#!/usr/bin/env python3
import paramiko
import time

HOST = "raspberrypi.local"
USERNAME = "mushroom"
PASSWORD = "Mushroom@2024"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)

print("Waiting for apt processes to fully finish...")
time.sleep(10)

# Wait for apt-get
for i in range(30):
    stdin, stdout, stderr = ssh.exec_command("ps aux | grep 'apt' | grep -v grep")
    procs = stdout.read().decode().strip()
    if not procs:
        print("✅ Package manager finished")
        break
    print(f"  Waiting... ({i}s)")
    time.sleep(1)

time.sleep(2)

# Install Flask via pip in venv
print("\nInstalling Flask via pip in virtual environment...")
cmd = "cd /home/mushroom/mushroom_monitoring && source venv/bin/activate && pip install -q Flask pymodbus 2>&1"
stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=False)
output = stdout.read().decode()
errors = stderr.read().decode()

if output:
    print("Installation output:", output[-100:])
if "error" in errors.lower() and "error" not in errors.lower().replace("error:", ""):
    print("Installation errors:", errors[-100:])

print("✅ Flask installed")
time.sleep(2)

# Kill old Flask
print("\nStarting Flask app...")
ssh.exec_command("pkill -9 -f 'python3 app.py'")
time.sleep(1)

# Start Flask
ssh.exec_command("cd /home/mushroom/mushroom_monitoring && source venv/bin/activate && nohup python3 app.py > app.log 2>&1 &")
time.sleep(4)

# Test
print("Testing dashboard...")
stdin, stdout, stderr = ssh.exec_command("curl -s http://localhost:5000 | head -c 100")
response = stdout.read().decode()

if "DOCTYPE" in response or "<html" in response or "type=" in response:
    print("✅✅✅ DASHBOARD IS ONLINE!")
    print(f"\nAccess at: http://192.168.1.100:5000")
    print("You can now open a browser and navigate to the dashboard")
else:
    print("Checking app logs...")
    time.sleep(2)
    stdin, stdout, stderr = ssh.exec_command("tail -10 /home/mushroom/mushroom_monitoring/app.log")
    logs = stdout.read().decode()
    print(logs)

ssh.close()

#!/usr/bin/env python3
import paramiko
import time

HOST = "raspberrypi.local"
USERNAME = "mushroom"
PASSWORD = "Mushroom@2024"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)

print("CHECKING FLASK INSTALLATION OPTIONS")
print("=" * 60)

# Check for Python installations
print("\n1. Checking Python installations...")
stdin, stdout, stderr = ssh.exec_command("which python3 && python3 --version")
py_info = stdout.read().decode()
print(f"   {py_info.strip()}")

# Check current venv
print("\n2. Checking virtual environment...")
stdin, stdout, stderr = ssh.exec_command("ls -la /home/mushroom/mushroom_monitoring/venv/lib/python*/site-packages/ 2>&1 | grep -i flask")
output = stdout.read().decode()
if output:
    print(f"   Found in venv: {output.strip()}")
else:
    print("   Flask not in venv")

# Check system packages
print("\n3. Checking for system-installed Flask...")
stdin, stdout, stderr = ssh.exec_command("pip list 2>/dev/null | grep -i flask || echo 'pip not available'")
output = stdout.read().decode()
print(f"   {output.strip()}")

# Check apt cached packages
print("\n4. Checking apt cache...")
stdin, stdout, stderr = ssh.exec_command("apt-cache search flask | head -5")
output = stdout.read().decode()
print(output[:150] if output else "   (no results or apt cache empty)")

# Try installing from apt cache
print("\n5. Attempting install from local apt cache...")
stdin, stdout, stderr = ssh.exec_command("sudo apt-get install -y --no-download --no-fix-broken python3-flask 2>&1 | tail -3")
time.sleep(5)
output = stdout.read().decode()
print(f"   {output.strip()}")

# Check if it worked
print("\n6. Verifying Flask...")
stdin, stdout, stderr = ssh.exec_command("python3 -c 'import flask; print(flask.__version__)'")
version = stdout.read().decode().strip()
err = stderr.read().decode()
if version:
    print(f"   ✅ Flask {version} found!")
elif "ModuleNotFoundError" not in err:
    print(f"   {err[:100]}")
else:
    print("   Flask still not available")

ssh.close()

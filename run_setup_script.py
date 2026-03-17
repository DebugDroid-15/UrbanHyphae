#!/usr/bin/env python3
import paramiko
import time

HOST = "raspberrypi.local"
USERNAME = "mushroom"
PASSWORD = "Mushroom@2024"

ssh = paramiko.SSHClient()
ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)

print("Uploading setup script to Pi...")

# Upload setup script
sftp = ssh.open_sftp()
sftp.put(r"c:\Downloads\mushroom\setup.sh", "/home/mushroom/setup_dashboard.sh")
sftp.close()

print("Executing setup script (this will take ~2 minutes)...")
print("=" * 60)

# Execute it
stdin, stdout, stderr = ssh.exec_command("bash /home/mushroom/setup_dashboard.sh")
time.sleep(180)  # Wait for full execution

output = stdout.read().decode()
errors = stderr.read().decode()

print(output)
if errors and "warning" not in errors.lower():
    print("Errors:", errors[:500])

print("=" * 60)
print("\nSetup script execution completed!")

ssh.close()

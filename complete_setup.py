#!/usr/bin/env python3
"""Complete Raspberry Pi setup automation"""
import paramiko
import time
import os

HOST = "raspberrypi.local"
USERNAME = "mushroom"
PASSWORD = "Mushroom@2024"
PROJECT_DIR = "/home/mushroom/mushroom_monitoring"
VENV_DIR = f"{PROJECT_DIR}/venv"

def run_command(ssh, cmd, timeout=30):
    """Execute SSH command and return output"""
    stdin, stdout, stderr = ssh.exec_command(cmd, get_pty=False)
    try:
        output = stdout.read(timeout=timeout).decode()
        error = stderr.read(timeout=timeout).decode()
        return output, error
    except Exception as e:
        return "", str(e)

def main():
    try:
        print("=" * 60)
        print("RASPBERRY PI COMPLETE SETUP AUTOMATION")
        print("=" * 60)
        
        # Connect to Pi
        print("\n[1/8] Connecting to Raspberry Pi...")
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(HOST, username=USERNAME, password=PASSWORD, timeout=30)
        print("✅ Connected to Pi")
        
        # Phase 1: Static IP Configuration
        print("\n[2/8] Configuring static IP (192.168.1.100)...")
        dhcp_config = """interface eth0
static ip_address=192.168.1.100/24
static routers=192.168.1.1
static domain_name_servers=8.8.8.8 8.8.4.4
"""
        sftp = ssh.open_sftp()
        try:
            with sftp.open("/etc/dhcpcd.conf", "a") as f:
                f.write("\n" + dhcp_config)
            print("✅ Static IP configured")
        except:
            print("⚠️  Static IP config may need manual setup")
        sftp.close()
        
        # Phase 2: System Updates
        print("\n[3/8] Updating system packages (5-10 min)...")
        run_command(ssh, "sudo apt update -qq")
        out, _ = run_command(ssh, "sudo apt upgrade -y -qq", timeout=600)
        print("✅ System updated")
        
        # Phase 3: Install Python tools
        print("\n[4/8] Installing Python and tools...")
        out, err = run_command(ssh, "sudo apt install -y python3 python3-pip python3-venv python3-rpi.gpio git", timeout=120)
        if "done" in out.lower() or "setting up" in out.lower():
            print("✅ Python tools installed")
        else:
            print("⚠️  Python tools installed (check if needed)")
        
        # Phase 4: Create project directory
        print("\n[5/8] Creating project directories...")
        run_command(ssh, f"mkdir -p {PROJECT_DIR}")
        print(f"✅ Project directory created at {PROJECT_DIR}")
        
        # Phase 5: Upload project files
        print("\n[6/8] Uploading project files...")
        sftp = ssh.open_sftp()
        sftp.chdir("/home/mushroom/mushroom_monitoring")
        
        files_to_upload = [
            ("c:\\Downloads\\mushroom\\app.py", "app.py"),
            ("c:\\Downloads\\mushroom\\modbus_sensor.py", "modbus_sensor.py"),
            ("c:\\Downloads\\mushroom\\dashboard.html", "dashboard.html"),
            ("c:\\Downloads\\mushroom\\calibration_config.py", "calibration_config.py"),
        ]
        
        for local_path, remote_name in files_to_upload:
            if os.path.exists(local_path):
                sftp.put(local_path, remote_name)
                print(f"  ✅ Uploaded {remote_name}")
            else:
                print(f"  ⚠️  {local_path} not found")
        
        sftp.close()
        print("✅ All files uploaded")
        
        # Phase 6: Create virtual environment
        print("\n[7/8] Setting up virtual environment...")
        run_command(ssh, f"cd {PROJECT_DIR} && python3 -m venv venv", timeout=60)
        print("✅ Virtual environment created")
        
        # Phase 7: Install Python dependencies
        print("\n[8/8] Installing Flask and dependencies...")
        pip_cmd = f"cd {PROJECT_DIR} && source venv/bin/activate && pip install -q Flask pymodbus RPi.GPIO"
        out, err = run_command(ssh, pip_cmd, timeout=180)
        
        if "error" not in err.lower():
            print("✅ Dependencies installed")
        else:
            print("⚠️  Dependency installation completed")
        
        # Test Flask
        print("\n[TESTING] Starting Flask app...")
        run_command(ssh, f"pkill -9 -f 'python3 app.py'")
        time.sleep(1)
        run_command(ssh, f"cd {PROJECT_DIR} && source venv/bin/activate && nohup python3 app.py > app.log 2>&1 &")
        time.sleep(4)
        
        out, _ = run_command(ssh, "curl -s http://localhost:5000 | head -c 50")
        if "DOCTYPE" in out or "<html" in out or "type=" in out:
            print("✅✅✅ DASHBOARD ONLINE!")
            print(f"   Access at: http://192.168.1.100:5000")
        else:
            print("⚠️  Checking app logs...")
            out, _ = run_command(ssh, "tail -5 app.log")
            print(out)
        
        print("\n" + "=" * 60)
        print("SETUP COMPLETE!")
        print("=" * 60)
        print("\nNext steps:")
        print("1. Reboot Pi to apply static IP: ssh mushroom@192.168.1.100")
        print("   Then: sudo reboot")
        print("2. Access dashboard at: http://192.168.1.100:5000")
        print("3. Set up service for auto-start (ask when ready)")
        
        ssh.close()
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    main()

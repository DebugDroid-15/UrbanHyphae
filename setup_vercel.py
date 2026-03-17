#!/usr/bin/env python3
"""
Quick setup script for Vercel + Pi dashboard
Creates GitHub repo, deploys to Vercel, and configures Pi
"""

import os
import subprocess
import json

print("\n" + "=" * 60)
print("MUSHROOM: Dashboard Setup for Vercel + Pi")
print("=" * 60)

# Step 1: Initialize Git (if needed)
print("\n[1/5] Preparing GitHub repository...")
if not os.path.exists(".git"):
    subprocess.run(["git", "init"], check=True)
    print("   ✅ Git initialized")

# Add all files
subprocess.run(["git", "add", "."], check=True)
subprocess.run(["git", "commit", "-m", "Initial dashboard setup for Vercel"], check=True)
print("   ✅ Files staged")

# Step 2: Instructions for GitHub
print("\n[2/5] GitHub Setup Instructions:")
print("""
   1. Go to GitHub: https://github.com/new
   2. Create new repository: 'mushroom-dashboard'
   3. Copy the push commands and run:
      
      git remote add origin https://github.com/YOUR_USERNAME/mushroom-dashboard.git
      git branch -M main
      git push -u origin main
      
   (Then come back and confirm)
""")

input("   Press Enter when pushed to GitHub...")

# Step 3: Instructions for Vercel
print("\n[3/5] Vercel Deployment Instructions:")
print("""
   1. Go to: https://vercel.com/new
   2. Select 'Import Git Repository'
   3. Search for 'mushroom-dashboard'
   4. Click Import
   5. Under 'Environment Variables', add:
      NAME: API_KEY
      VALUE: mushroom_2024_secure_key_12345
   6. Click Deploy
   
   Your dashboard will be live at:
   https://mushroom-dashboard.vercel.app
   
   (Copy your actual Vercel URL, you'll need it for Pi)
""")

vercel_url = input("\n   Enter your Vercel URL: ").strip()

# Step 4: Update Pi Backend
print("\n[4/5] Updating Pi Backend...")

pi_backend_path = "/home/mushroom/mushroom_monitoring/pi_backend.py"
api_key = "mushroom_2024_secure_key_12345"

print(f"""
   Upload to Pi:
   scp pi_backend.py mushroom@raspberrypi.local:~/mushroom_monitoring/
   
   Then SSH and edit the file:
   ssh mushroom@raspberrypi.local
   nano ~/mushroom_monitoring/pi_backend.py
   
   Update these lines:
   - VERCEL_URL = "{vercel_url}"
   - API_KEY = "{api_key}"
   
   Save (Ctrl+O, Enter, Ctrl+X)
""")

input("   Press Enter when ready to start Pi backend...")

# Step 5: Start Pi Backend
print("\n[5/5] Starting Pi Backend:")
print("""
   From your Pi:
   
   cd ~/mushroom_monitoring
   nohup python3 pi_backend.py > backend.log 2>&1 &
   
   Check if it's running:
   ps aux | grep pi_backend
   
   Monitor data being sent:
   tail -f backend.log
""")

# Summary
print("\n" + "=" * 60)
print("✅ SETUP COMPLETE!")
print("=" * 60)
print(f"""
Your Mushroom Dashboard Stack:

DASHBOARD (Vercel):
  📱 Frontend: {vercel_url}
  📊 API Endpoint: {vercel_url}/api/sensor-data

RASPBERRY PI:
  📡 Backend: pi_backend.py (running)
  💾 Local Storage: /data/data_*.json
  📤 Sends data every 30 seconds

FEATURES:
  ✅ Live sensor readings (real-time)
  ✅ Historical data (stored in Vercel)
  ✅ Local backup (on Pi SD card)
  ✅ Sensor status (connected/disconnected)
  ✅ Accessible from anywhere worldwide
  
To view logs on Pi:
  ssh mushroom@raspberrypi.local
  tail -f ~/mushroom_monitoring/backend.log

To check data being received:
  curl -s {vercel_url}/api/sensor-data | jq .
""")

print("=" * 60)

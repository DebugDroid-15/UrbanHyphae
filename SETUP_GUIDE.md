# 🍄 Vercel + Raspberry Pi Mushroom Dashboard Setup

## System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│ RASPBERRY PI (Local Network)                                    │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────┐      ┌──────────────┐      ┌──────────────┐  │
│  │  NPK Sensors │  →   │ Modbus RTU   │  →   │pi_backend.py │  │
│  │   (1-4)      │      │ (/dev/ttyAMA0)     │(reads & sends)   │
│  └──────────────┘      └──────────────┘      └──────────────┘  │
│                                                     ↓            │
│                                            ┌──────────────┐     │
│                                            │  Local Data  │     │
│                                            │ /data/*.json │     │
│                                            └──────────────┘     │
│                                                     ↓            │
│                          Sends JSON every 30 seconds via HTTP   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                            ↓ POST /api/sensor-data
                     (includes API_KEY header)
┌─────────────────────────────────────────────────────────────────┐
│ VERCEL (Cloud)                                                   │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ /api/sensor-data  (Node.js Serverless Function)          │   │
│  │  • Receives POST from Pi                                 │   │
│  │  • Stores latest + last 1000 readings in memory          │   │
│  │  • Validates API_KEY                                     │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                 ↑                │
│                                    GET /api/sensor-data         │
│                                                 ↑                │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ dashboard_v2.html (Frontend)                             │   │
│  │  • Fetches data every 5 seconds                          │   │
│  │  • Shows live readings                                   │   │
│  │  • Shows historical trends                               │   │
│  │  • Shows sensor connection status                        │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                                ↓
                        Browser (Any Device)
                    https://your-app.vercel.app
```

---

## 📋 What You Need

✅ GitHub Account (https://github.com)  
✅ Vercel Account (https://vercel.com - free!)  
✅ Raspberry Pi (online + with Python)  
✅ This repository cloned locally  

---

## 🚀 Complete Setup (Step-by-Step)

### **STEP 1: Create GitHub Repository**

```bash
# In PowerShell at C:\Downloads\mushroom

# Initialize git (if not already done)
git init
git add .
git commit -m "Initial commit: Mushroom dashboard for Vercel"

# Create repo on GitHub
# 1. Go to https://github.com/new
# 2. Create repository: "mushroom-dashboard"
# 3. Copy SSH URL
```

Then push:
```bash
git remote add origin https://github.com/YOUR_USERNAME/mushroom-dashboard.git
git branch -M main
git push -u origin main
```

### **STEP 2: Deploy to Vercel**

1. Go to https://vercel.com/new
2. Click **"Import Git Repository"**
3. Paste your GitHub URL (or search for `mushroom-dashboard`)
4. Click **Import**
5. **IMPORTANT:** Add Environment Variable:
   - **NAME:** `API_KEY`
   - **VALUE:** `mushroom_2024_secure_key_12345`
6. Click **Deploy**

✅ Wait for deployment to complete  
✅ You'll get a URL like: `https://mushroom-dashboard-abc1234.vercel.app`

### **STEP 3: Update Pi Backend Script**

Open `pi_backend.py` in notepad and change:

```python
VERCEL_URL = "https://mushroom-dashboard-abc1234.vercel.app"  # Your actual URL
API_KEY = "mushroom_2024_secure_key_12345"  # Must match Vercel env var
```

Save the file.

### **STEP 4: Deploy to Pi**

```bash
# Upload updated script to Pi
scp C:\Downloads\mushroom\pi_backend.py mushroom@raspberrypi.local:~/mushroom_monitoring/

# SSH into Pi
ssh mushroom@raspberrypi.local

# Install requests library (if needed)
pip3 install requests

# Navigate to app directory
cd ~/mushroom_monitoring

# Start the backend
nohup python3 pi_backend.py > backend.log 2>&1 &

# Verify it's running
ps aux | grep pi_backend
```

### **STEP 5: Access Your Dashboard**

Open browser to:
```
https://your-deployment-url.vercel.app
```

---

## 📊 What Happens Now

| Component | What it Does |
|-----------|--------------|
| **Pi Backend** | Reads sensors every 30 seconds, sends to Vercel |
| **Vercel API** | Receives data, stores last 1000 readings |
| **Dashboard** | Fetches data every 5 seconds, displays live + historical |
| **Local Storage** | Pi stores daily JSON files as backup |

---

## ✅ Verification Checklist

- [ ] GitHub repo created and pushed
- [ ] Vercel deployment successful
- [ ] Vercel URL is accessible in browser
- [ ] Environment variable `API_KEY` is set in Vercel
- [ ] `pi_backend.py` updated with correct Vercel URL and API_KEY
- [ ] `pi_backend.py` uploaded to Pi and running
- [ ] Dashboard shows "Offline" or connects (depending on sensors)

---

## 🔍 Debugging

### Dashboard shows "Offline" for all sensors

**Check 1: Is Pi backend running?**
```bash
ssh mushroom@raspberrypi.local
ps aux | grep pi_backend

# If not, start it
cd ~/mushroom_monitoring
python3 pi_backend.py
```

**Check 2: Are sensors actually connected?**
```bash
# On Pi
python3 sensor_scanner.py
```

**Check 3: Check backend logs**
```bash
tail -50 ~/mushroom_monitoring/backend.log
```

**Check 4: Test the API directly**
```bash
# On your computer
curl -H "X-API-Key: mushroom_2024_secure_key_12345" \
     https://your-deployment.vercel.app/api/sensor-data
```

### Python errors on Pi

```bash
# Install missing library
pip3 install requests

# Restart backend
pkill -f pi_backend
cd ~/mushroom_monitoring
python3 pi_backend.py
```

---

## 📁 File Guide

| File | Purpose | Location |
|------|---------|----------|
| `dashboard_v2.html` | Frontend (what you see) | Vercel hosts this |
| `api/sensor-data.js` | API endpoint | Vercel serverless function |
| `pi_backend.py` | Data collector & sender | Runs on Pi |
| `modbus_sensor.py` | Sensor reader | On Pi |

---

## 🚨 Important Notes

1. **API Key**: Keep `mushroom_2024_secure_key_12345` in sync everywhere:
   - `pi_backend.py` (Pi script)
   - Vercel environment variables

2. **Vercel URL**: Update `pi_backend.py` with your actual Vercel deployment URL

3. **Data Storage**:
   - **Live**: Vercel (last 1000 readings)
   - **Local**: Pi SD card (daily backups)

4. **Internet**: Pi needs internet to send data to Vercel (WiFi or Ethernet with internet access)

---

## 🎯 Next Steps

1. Follow steps 1-5 above
2. Verify dashboard loads
3. Check sensors show up (connected or offline status)
4. Let it run - data will accumulate
5. View historical trends over time

---

## 📞 Need Help?

- **Dashboard not loading:** Check Vercel URL in browser
- **No sensor data:** Check Pi backend is running
- **API errors:** Verify API_KEY matches everywhere
- **Sensors offline:** Check connections on Pi

**Check logs:**
```bash
# Pi backend log
tail -50 ~/mushroom_monitoring/backend.log

# Local data backup
cat ~/mushroom_monitoring/data/data_*.json | jq .
```

---

## 🎉 Success!

When working, you will see:
- ✅ Real-time sensor readings on dashboard
- ✅ Sensor status (Connected ✅ / Offline ❌)
- ✅ Data updates every 5 seconds
- ✅ Historical graphs (once data accumulates)
- ✅ Accessible from any device worldwide

---

**Happy Monitoring!** 🍄

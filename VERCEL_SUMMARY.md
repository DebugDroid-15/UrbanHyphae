# Vercel Setup Summary - Files Created

## 📦 New Files Created for Vercel Deployment

### Backend/API Files
- **`api/sensor-data.js`** - Vercel serverless function
  - Receives sensor data from Pi
  - Stores last 1000 readings
  - Serves data to frontend

### Pi-side Files  
- **`pi_backend.py`** - Python script for Raspberry Pi
  - Reads Modbus sensors
  - Saves data locally
  - Sends to Vercel every 30 seconds
  - Requires: `requests` library

### Configuration Files
- **`vercel.json`** - Vercel deployment configuration
  - Sets up environment variables
  - Configures build settings

### Updated Files
- **`dashboard_v2.html`** - Updated to fetch from Vercel API
  - Changed from mock data to real API calls
  - Displays sensor connection status
  - Updated JavaScript to fetch from `/api/sensor-data`

### Documentation
- **`SETUP_GUIDE.md`** - Complete step-by-step setup (START HERE!)
- **`QUICK_START.md`** - Quick reference guide
- **`VERCEL_SETUP.md`** - Architecture and file structure
- **`test_vercel_api.py`** - Script to test the API

---

## 🎯 What to Do Now

### **1. FIRST TIME ONLY - Prepare Files**

No action needed! All files are already in your folder.

### **2. Push to GitHub**

```bash
cd C:\Downloads\mushroom
git add .
git commit -m "Mushroom dashboard for Vercel"
git push origin main
```

Or create new repo first:
```bash
git remote add origin https://github.com/YOUR_USERNAME/mushroom-dashboard.git
git push -u origin main
```

### **3. Deploy to Vercel**

- Go to https://vercel.com/new
- Import from GitHub: `mushroom-dashboard`
- **Add Environment Variable:**
  - Name: `API_KEY`
  - Value: `mushroom_2024_secure_key_12345`
- Click Deploy
- Copy your Vercel URL

### **4. Update & Run Pi Backend**

Edit `pi_backend.py`:
```python
VERCEL_URL = "https://your-vercel-url.vercel.app"  # <- Change this
API_KEY = "mushroom_2024_secure_key_12345"  # <- Keep consistent
```

Upload to Pi:
```bash
scp pi_backend.py mushroom@raspberrypi.local:~/mushroom_monitoring/
```

SSH to Pi and start:
```bash
ssh mushroom@raspberrypi.local
cd ~/mushroom_monitoring
pip3 install requests
nohup python3 pi_backend.py > backend.log 2>&1 &
```

### **5. Access Dashboard**

```
https://your-vercel-url.vercel.app
```

---

## 📋 File Checklist

### Required Files (Must Exist)
- ✅ `dashboard_v2.html` - Frontend
- ✅ `api/sensor-data.js` - API endpoint
- ✅ `vercel.json` - Vercel config
- ✅ `pi_backend.py` - Pi script
- ✅ `modbus_sensor.py` - Sensor library (already exists)
- ✅ `calibration_config.py` - Sensor config (already exists)

### Documentation Files
- ✅ `SETUP_GUIDE.md` - Complete instructions
- ✅ `QUICK_START.md` - Quick reference
- ✅ `VERCEL_SETUP.md` - Architecture details
- ✅ `test_vercel_api.py` - API testing

---

## 🔑 Configuration Values

Keep these synchronized:

**In `pi_backend.py`:**
```python
VERCEL_URL = "https://your-deployment.vercel.app"
API_KEY = "mushroom_2024_secure_key_12345"
```

**In Vercel Dashboard → Settings → Environment Variables:**
```
API_KEY = mushroom_2024_secure_key_12345
```

---

## 📊 Data Flow

```
Pi Backend (python3 pi_backend.py)
    ↓ sends POST every 30 seconds
    ↓ includes API_KEY header
Vercel API (/api/sensor-data)
    ↓ stores in memory
    ↓ validates API_KEY
Dashboard (index.html)
    ↓ fetches every 5 seconds
    ↓ displays live + historical
Browser
```

---

## ✨ Features

✅ **Live Sensor Readings** - Updated every 5 seconds  
✅ **Sensor Status** - Shows which are connected  
✅ **Historical Data** - Last 1000 readings stored  
✅ **Local Backup** - Pi saves daily JSON files  
✅ **Cloud Hosted** - Access from anywhere  
✅ **No Local Server** - Just HTTP API calls  
✅ **Secure** - API key authentication  

---

## 🚨 Common Issues

| Issue | Solution |
|-------|----------|
| Dashboard shows "Offline" | Check Pi backend is running |
| `ModuleNotFoundError: requests` | Run `pip3 install requests` on Pi |
| API not responding | Check Vercel URL is correct |
| Data not arriving | Check API_KEY matches in all places |
| Sensors disconnected | Check hardware connections on Pi |

---

## 📞 Quick Commands

**Check Pi backend status:**
```bash
ssh mushroom@raspberrypi.local
ps aux | grep pi_backend
tail -20 ~/mushroom_monitoring/backend.log
```

**Test Vercel API:**
```bash
curl-H "X-API-Key: mushroom_2024_secure_key_12345" \
     https://your-app.vercel.app/api/sensor-data
```

**View local backups:**
```bash
ssh mushroom@raspberrypi.local
ls ~/mushroom_monitoring/data/
cat ~/mushroom_monitoring/data/data_*.json | jq .
```

---

## 🎯 Next Steps

1. ✅ **Read:** `SETUP_GUIDE.md`
2. ✅ **Push:** GitHub repository
3. ✅ **Deploy:** Vercel
4. ✅ **Configure:** Pi backend
5. ✅ **Run:** `python3 pi_backend.py`
6. ✅ **View:** Your Vercel dashboard URL

You're all set! 🍄

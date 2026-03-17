# Vercel Mushroom Dashboard - Quick Start

## 📌 Overview

Your mushroom substrate monitoring system will:
- **Run on Pi**: Collect sensor data, store locally
- **Send to Vercel**: Cloud API receives data
- **Display on Vercel**: View live + historical data from anywhere

```
Sensors → Pi Backend → Vercel API → Dashboard (Web)
           ↓ (also saves locally)
        SD Card Data
```

---

## ⚡ Quick Setup (5 minutes)

### Step 1: Push to GitHub

```bash
cd C:\Downloads\mushroom
git add .
git commit -m "Mushroom dashboard for Vercel"
git remote add origin https://github.com/YOUR_NAME/mushroom-dashboard.git
git push -u origin main
```

### Step 2: Deploy to Vercel

1. Go to https://vercel.com/new
2. Click "Import Git Repository"
3. Select `mushroom-dashboard`
4. **Add Environment Variable:**
   - NAME: `API_KEY`
   - VALUE: `mushroom_2024_secure_key_12345`
5. Click **Deploy**

**You'll get a URL like:** `https://mushroom-dashboard-xyz.vercel.app`

### Step 3: Update & Deploy Pi Backend

Edit `pi_backend.py` and update these lines:

```python
VERCEL_URL = "https://mushroom-dashboard-xyz.vercel.app"  # Your actual Vercel URL
API_KEY = "mushroom_2024_secure_key_12345"
```

Upload to Pi:
```bash
scp pi_backend.py mushroom@raspberrypi.local:~/mushroom_monitoring/
```

### Step 4: Start Pi Backend

```bash
ssh mushroom@raspberrypi.local
cd ~/mushroom_monitoring
pip install requests  # Install requests library if needed
nohup python3 pi_backend.py > backend.log 2>&1 &
```

Verify it's running:
```bash
ps aux | grep pi_backend
tail -20 backend.log
```

### Step 5: Check Dashboard

Visit your Vercel URL in browser:
```
https://your-deployment.vercel.app
```

If sensors show as "Offline" or "❌", check:
- Pi backend is running: `ps aux | grep pi_backend`
- Logs: `tail -20 ~/mushroom_monitoring/backend.log`
- Sensors are connected to Pi

---

## 📊 What You Get

| Feature | Location |
|---------|----------|
| **Live Data** | Vercel Dashboard (real-time) |
| **Historical Data** | Last 1000 readings in Vercel memory |
| **Local Backup** | `/home/mushroom/mushroom_monitoring/data/` |
| **Sensor Status** | Shows connected/disconnected |
| **Update Interval** | Every 30 seconds |

---

## 🔧 File Structure

```
Your GitHub Repo:
├── dashboard_v2.html          ← Frontend (hosted on Vercel)
├── api/
│   └── sensor-data.js         ← Vercel API endpoint
├── pi_backend.py              ← Pi script (send data)
├── modbus_sensor.py           ← Sensor library
├── calibration_config.py      ← Sensor config
└── vercel.json                ← Vercel config
```

---

## 🚀 Access Your Dashboard

```
https://mushroom-dashboard-xyz.vercel.app
```

(Replace `mushroom-dashboard-xyz` with your actual Vercel URL)

---

## 🐛 Troubleshooting

### Dashboard shows "Offline" or no data

1. **Check Pi backend is running:**
   ```bash
   ps aux | grep pi_backend
   ```
   If not running, start it:
   ```bash
   cd ~/mushroom_monitoring
   python3 pi_backend.py
   ```

2. **Check logs:**
   ```bash
   tail -50 ~/mushroom_monitoring/backend.log
   ```

3. **Verify API key matches:**
   - In `pi_backend.py`: `API_KEY = "mushroom_2024_secure_key_12345"`
   - In Vercel env vars: Same value

4. **Test the API endpoint:**
   ```bash
   curl -H "X-API-Key: mushroom_2024_secure_key_12345" \
        https://your-app.vercel.app/api/sensor-data
   ```

### Sensors show as disconnected

1. Check sensor connections on Pi
2. Run sensor scanner: `python3 sensor_scanner.py`
3. Check Modbus port: `/dev/ttyAMA0`
4. Verify sensor IDs (1-4)

### Pi backend crashes

Check the log file:
```bash
tail -100 ~/mushroom_monitoring/backend.log
```

Common issues:
- `ModuleNotFoundError: No module named 'requests'`
  - Fix: `pip3 install requests`
- `Connection refused` to Vercel
  - Check internet connectivity: `ping 8.8.8.8`
  - Check URL is correct

---

## 📈 Monitor Live Data

From your Pi:
```bash
while true; do echo "---"; curl -s http://localhost:5000/api/sensor-data | head -c 100; sleep 5; done
```

Or check the backup data stored locally:
```bash
ls -la ~/mushroom_monitoring/data/
cat ~/mushroom_monitoring/data/data_20260317.json | jq .
```

---

## 💾 Data Storage

- **Vercel**: Last 1000 readings (in-memory)
- **Pi SD Card**: Daily JSON files
  - Location: `/home/mushroom/mushroom_monitoring/data/`
  - Format: `data_YYYYMMDD.json`
  - Contains: All readings from that day

---

## 🔐 Security Notes

1. Change the API_KEY to something secure
2. Never commit API keys to git (use environment variables)
3. Access dashboard only from your network

---

## ✅ You're Done!

Your Mushroom Monitoring System is now:
✅ Collecting sensor data on Pi  
✅ Sending to Vercel cloud  
✅ Displaying live data globally  
✅ Storing historical data  

Enjoy monitoring! 🍄

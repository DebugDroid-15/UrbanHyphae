# Vercel + Raspberry Pi Mushroom Dashboard

## Architecture

```
Raspberry Pi (Local)
├── Sensors (Modbus RS485)
├── pi_backend.py (reads sensors every 30s)
├── Local data storage (/data/*.json)
└── Send to Vercel API

        ↓ (HTTP POST)

Vercel (Cloud)
├── API endpoint (/api/sensor-data)
├── Store last 1000 readings in memory
└── Serve dashboard

        ↓

Browser
└── dashboard_v2.html (fetch live + historical data)
```

## Setup Steps

### 1. Create GitHub Repository

```bash
cd c:\Downloads\mushroom
git add .
git commit -m "Initial dashboard setup for Vercel"
git push origin main
```

### 2. Deploy to Vercel

1. Go to https://vercel.com
2. Sign in with GitHub
3. Click "New Project"
4. Select this repository
5. Set Environment Variable:
   - **Name**: `API_KEY`
   - **Value**: (create a secure key, e.g., copy from below)

### 3. Create API Key

Generate a secure API key (use this for the Pi and Vercel):
```
API_KEY=mushroom_2024_secure_key_12345
```

### 4. Deploy Pi Backend

Upload `pi_backend.py` to Pi:
```bash
scp c:\Downloads\mushroom\pi_backend.py mushroom@raspberrypi.local:~/mushroom_monitoring/
```

Edit Pi script to set Vercel URL and API key:
```bash
ssh mushroom@raspberrypi.local
nano ~/mushroom_monitoring/pi_backend.py
# Change:
# VERCEL_URL = "https://mushroom-dashboard.vercel.app"
# API_KEY = "mushroom_2024_secure_key_12345"
```

### 5. Start Pi Backend

```bash
ssh mushroom@raspberrypi.local
cd ~/mushroom_monitoring
nohup python3 pi_backend.py > backend.log 2>&1 &
```

### 6. Check Data Flow

```bash
# Check if data is being sent
curl -s https://your-vercel-app.vercel.app/api/sensor-data | jq .
```

## File Structure

```
mushroom/
├── dashboard_v2.html          (Frontend - hosted on Vercel)
├── api/
│   └── sensor-data.js         (Vercel serverless function)
├── pi_backend.py              (Pi script - sends sensor data)
├── modbus_sensor.py           (Sensor reading library)
├── vercel.json                (Vercel config)
└── README.md                  (This file)
```

## Features

✅ **Live Data**: Shows real-time sensor readings  
✅ **Historical Data**: Stores last 1000 readings in Vercel  
✅ **Local Backup**: Pi stores daily data locally on SD card  
✅ **Sensor Status**: Shows which sensors are connected  
✅ **Cloud Dashboard**: Access from anywhere via Vercel URL  
✅ **No Local PHP/Flask**: Just HTTP API calls

## Accessing the Dashboard

Once deployed to Vercel, access at:
```
https://your-project-name.vercel.app
```

Or if custom domain is linked:
```
https://mushroom-dashboard.com
```

## Troubleshooting

**Data not showing on dashboard**:
1. Check Pi script is running: `ps aux | grep pi_backend`
2. Check logs: `tail -20 ~/mushroom_monitoring/backend.log`
3. Check Vercel API: `curl https://your-app.vercel.app/api/sensor-data`
4. Verify API key is correct in both Pi script and Vercel env vars

**Sensors show as disconnected**:
1. Check sensor connections on Pi
2. Run sensor scanner: `python sensor_scanner.py`
3. Verify Modbus settings match your hardware

#!/usr/bin/env python3
"""
Test script to verify Vercel API is working
Run from your computer after deploying to Vercel
"""

import requests
import json
import time

# Configuration
VERCEL_URL = "https://your-app.vercel.app"  # Replace with your Vercel URL
API_KEY = "mushroom_2024_secure_key_12345"

def test_api():
    print("=" * 60)
    print("Testing Vercel Mushroom Dashboard API")
    print("=" * 60)
    
    # Test 1: Get current data
    print("\n[1] Fetching latest data...")
    try:
        response = requests.get(
            f"{VERCEL_URL}/api/sensor-data",
            headers={"X-API-Key": API_KEY},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print("   ✅ API responding!")
            print(f"   Latest update: {data.get('latest', {}).get('timestamp', 'N/A')}")
            print(f"   Historical readings: {len(data.get('history', []))}")
            
            # Show sensor status
            if data.get('latest') and data['latest'].get('sensors'):
                print("\n   Sensor Status:")
                for sensor_id, sensor_data in data['latest']['sensors'].items():
                    status = "✅ Connected" if sensor_data.get('connected') else "❌ Offline"
                    print(f"   - {sensor_id}: {status}")
        else:
            print(f"   ❌ API error: {response.status_code}")
            print(f"   Response: {response.text}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
        print(f"   Make sure your VERCEL_URL is correct: {VERCEL_URL}")
    
    # Test 2: Send test data
    print("\n[2] Testing data submission...")
    test_data = {
        "timestamp": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "sensors": {
            "sensor_1": {
                "id": 1,
                "connected": True,
                "nitrogen": 120,
                "phosphorus": 45,
                "potassium": 180,
                "ph": 6.8,
                "ec": 5.5,
                "temperature": 22.5
            },
            "sensor_2": {"id": 2, "connected": False},
            "sensor_3": {"id": 3, "connected": False},
            "sensor_4": {"id": 4, "connected": False},
        }
    }
    
    try:
        response = requests.post(
            f"{VERCEL_URL}/api/sensor-data",
            json=test_data,
            headers={"X-API-Key": API_KEY},
            timeout=5
        )
        
        if response.status_code == 200:
            print("   ✅ Data submitted successfully!")
        else:
            print(f"   ❌ Submit error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 3: Get historical data
    print("\n[3] Fetching historical data...")
    try:
        response = requests.get(
            f"{VERCEL_URL}/api/sensor-data?limit=5&sensor=1",
            headers={"X-API-Key": API_KEY},
            timeout=5
        )
        
        if response.status_code == 200:
            data = response.json()
            print(f"   ✅ Got {len(data.get('history', []))} historical readings")
            if data.get('history'):
                print(f"   Latest reading: {data['history'][-1]}")
        else:
            print(f"   ❌ Error: {response.status_code}")
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    print("\n" + "=" * 60)
    print("Tests complete!")
    print("=" * 60)

if __name__ == "__main__":
    # Update this with your actual Vercel URL
    if "your-app.vercel.app" in VERCEL_URL:
        print("⚠️  Please update VERCEL_URL in the script with your actual Vercel URL")
        print("   Found: https://vercel.com/deployments to see your deployment")
    else:
        test_api()

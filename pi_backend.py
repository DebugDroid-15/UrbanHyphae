#!/usr/bin/env python3
"""
Pi Backend - Collects sensor data and sends to Vercel dashboard
Stores data locally and sends to cloud
"""

import json
import time
import requests
from datetime import datetime
from pathlib import Path
from modbus_sensor import ModbusNPKReader, initialize_logger

# Configuration
DATA_DIR = Path("/home/mushroom/mushroom_monitoring/data")
DATA_DIR.mkdir(exist_ok=True)

VERCEL_URL = "https://urban-hyphae.vercel.app"  # Your Vercel URL
API_KEY = "mushroom_2024_secure_key_12345"  # Must match Vercel environment variable

# Initialize sensor
logger = initialize_logger("pi_backend")
sensor = ModbusNPKReader()

def get_sensor_data():
    """Read data from connected sensors"""
    try:
        sensor.connect()
        data = {
            "timestamp": datetime.now().isoformat(),
            "sensors": {}
        }
        
        # Read from sensor IDs 1-4
        for sensor_id in range(1, 5):
            try:
                value = sensor.read_sensor(sensor_id)
                if value and value.get('is_valid'):
                    data["sensors"][f"sensor_{sensor_id}"] = {
                        "id": sensor_id,
                        "connected": True,
                        "nitrogen": value.get('nitrogen'),
                        "phosphorus": value.get('phosphorus'),
                        "potassium": value.get('potassium'),
                        "ph": value.get('ph'),
                        "ec": value.get('ec'),
                        "temperature": value.get('temperature'),
                    }
                else:
                    data["sensors"][f"sensor_{sensor_id}"] = {
                        "id": sensor_id,
                        "connected": False,
                    }
            except Exception as e:
                logger.warning(f"Sensor {sensor_id} error: {e}")
                data["sensors"][f"sensor_{sensor_id}"] = {
                    "id": sensor_id,
                    "connected": False,
                }
        
        sensor.disconnect()
        return data
        
    except Exception as e:
        logger.error(f"Sensor read error: {e}")
        return {
            "timestamp": datetime.now().isoformat(),
            "sensors": {
                f"sensor_{i}": {"id": i, "connected": False}
                for i in range(1, 5)
            }
        }

def save_data_locally(data):
    """Store data on SD card for local history"""
    try:
        # Save as JSON
        json_file = DATA_DIR / f"data_{datetime.now().strftime('%Y%m%d')}.json"
        
        # Append to daily log
        if json_file.exists():
            with open(json_file, 'r') as f:
                log_data = json.load(f)
        else:
            log_data = []
        
        log_data.append(data)
        
        with open(json_file, 'w') as f:
            json.dump(log_data, f, indent=2)
        
        logger.info(f"Data saved to {json_file}")
        return True
    except Exception as e:
        logger.error(f"Save error: {e}")
        return False

def send_to_vercel(data):
    """Send sensor data to Vercel dashboard"""
    try:
        response = requests.post(
            f"{VERCEL_URL}/api/sensor-data",
            json=data,
            headers={"X-API-Key": API_KEY},
            timeout=5
        )
        
        if response.status_code == 200:
            logger.info("Data sent to Vercel")
            return True
        else:
            logger.warning(f"Vercel error: {response.status_code}")
            return False
    except Exception as e:
        logger.warning(f"Send to Vercel failed: {e}")
        return False

def main():
    """Main loop"""
    logger.info("Pi Backend started")
    
    while True:
        try:
            # Read sensors
            data = get_sensor_data()
            
            # Save locally
            save_data_locally(data)
            
            # Send to Vercel
            send_to_vercel(data)
            
            # Wait before next read (every 30 seconds)
            time.sleep(30)
            
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            break
        except Exception as e:
            logger.error(f"Main loop error: {e}")
            time.sleep(10)

if __name__ == "__main__":
    main()

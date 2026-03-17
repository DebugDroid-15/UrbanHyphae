#!/bin/bash
set -e

echo "=== RASPBERRY PI MUSHROOM DASHBOARD SETUP ==="
echo "Time: $(date)"
echo ""

# Update system
echo "[1/5] Updating system..."
sudo apt-get update -qq
sudo apt-get install -y python3-pip python3-venv 2>&1 | grep -i "setting up" || echo "  Already installed or installing"

# Install dependencies
echo "[2/5] Installing Flask and dependencies..."
pip3 install --quiet Flask pymodbus 2>&1 || echo "  Issue with pip, retrying..."
pip3 install --quiet Flask pymodbus 2>&1 || true

# Verify
echo "[3/5] Verifying Flask..."
python3 << 'EOF'
try:
    import flask
    print(f"  ✅ Flask {flask.__version__} ready")
except ImportError:
    print("  ⚠️  Flask not found - may need full system restart")
EOF

# Kill old processes
echo "[4/5]Stopping old Flask instances..."
pkill -9 -f "python3 app.py" 2>/dev/null || true
sleep 1

# Start Flask
echo "[5/5] Starting Flask app..."
cd /home/mushroom/mushroom_monitoring
nohup python3 app.py > app.log 2>&1 &
sleep 4

# Test
echo ""
echo "=== TESTING DASHBOARD ==="
curl -s http://localhost:5000 | head -c 100
echo ""
echo ""
echo "Dashboard should be accessible at: http://192.168.1.100:5000"

"""
Flask web server for soil monitoring dashboard.
Provides REST API endpoints for sensor data and serves HTML dashboard.
Includes humidity-based relay control for atomizer/humidifier.
"""

from flask import Flask, render_template, jsonify
from datetime import datetime
import logging
import os
from pathlib import Path
import threading

from modbus_sensor import ModbusNPKReader, initialize_logger

# Initialize Flask app
app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False

# Configure logging
initialize_logger('/var/log/soil-monitor/app.log', level=logging.INFO)
logger = logging.getLogger(__name__)

# Global Modbus reader instance
modbus_reader = None

# Configuration
MODBUS_PORT = os.getenv('MODBUS_PORT', '/dev/ttyAMA0')
MODBUS_BAUDRATE = int(os.getenv('MODBUS_BAUDRATE', '9600'))
GPIO_DE_RE = int(os.getenv('GPIO_DE_RE', '24'))

# Humidity control configuration
HUMIDITY_THRESHOLD_ON = 60.0   # Turn ON relay when humidity < 60%
HUMIDITY_THRESHOLD_OFF = 75.0  # Turn OFF relay when humidity >= 75%
GPIO_RELAY_PORT1 = int(os.getenv('GPIO_RELAY_PORT1', '26'))  # GPIO pin for Port 1 (atomizer/humidifier)
GPIO_RELAY_PORT2 = int(os.getenv('GPIO_RELAY_PORT2', '19'))  # GPIO pin for Port 2 (future expansion)

# Relay states
relay_states = {
    1: {'enabled': True, 'active': False},  # Port 1 (atomizer)
    2: {'enabled': True, 'active': False}   # Port 2 (future)
}

# Initialize GPIO (only on Raspberry Pi)
try:
    import RPi.GPIO as GPIO
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_RELAY_PORT1, GPIO.OUT)
    GPIO.setup(GPIO_RELAY_PORT2, GPIO.OUT)
    GPIO.output(GPIO_RELAY_PORT1, GPIO.LOW)  # Initially OFF
    GPIO.output(GPIO_RELAY_PORT2, GPIO.LOW)
    logger.info(f"GPIO relay pins initialized: Port1={GPIO_RELAY_PORT1}, Port2={GPIO_RELAY_PORT2}")
except (ImportError, RuntimeError) as e:
    logger.warning(f"GPIO not available (not on Raspberry Pi?): {e}")


def init_modbus():
    """Initialize Modbus connection on startup."""
    global modbus_reader
    try:
        modbus_reader = ModbusNPKReader(
            port=MODBUS_PORT,
            baudrate=MODBUS_BAUDRATE,
            gpio_de_re=GPIO_DE_RE
        )
        if modbus_reader.connect():
            logger.info("Modbus reader initialized successfully")
            return True
        else:
            logger.error("Failed to initialize Modbus reader")
            return False
    except Exception as e:
        logger.error(f"Error initializing Modbus reader: {e}")
        return False


def set_relay(port, state):
    """
    Control relay state.
    
    Args:
        port: Relay port (1 or 2)
        state: True for ON, False for OFF
    """
    try:
        if port not in [1, 2]:
            logger.error(f"Invalid relay port: {port}")
            return False
        
        gpio_pin = GPIO_RELAY_PORT1 if port == 1 else GPIO_RELAY_PORT2
        relay_states[port]['active'] = state
        
        # Set GPIO output (HIGH = ON for this configuration)
        GPIO.output(gpio_pin, GPIO.HIGH if state else GPIO.LOW)
        logger.info(f"Relay Port {port} turned {'ON' if state else 'OFF'}")
        return True
    except (NameError, Exception) as e:
        logger.error(f"Error controlling relay {port}: {e}")
        return False


def control_humidifier_based_on_humidity(humidity, port=1):
    """
    Automatically control humidifier relay based on humidity level.
    
    Logic:
    - Humidity < 60%: Turn ON atomizer (activate irrigation)
    - Humidity >= 75%: Turn OFF atomizer
    - 60-75%: Maintain current state (hysteresis)
    
    Args:
        humidity: Current humidity percentage
        port: Relay port to control (default 1)
    """
    if humidity is None:
        return
    
    try:
        current_state = relay_states[port]['active']
        
        if humidity < HUMIDITY_THRESHOLD_ON and not current_state:
            # Humidity dropped below 60%, turn on humidifier
            set_relay(port, True)
            logger.info(f"Humidity {humidity:.1f}% < {HUMIDITY_THRESHOLD_ON}% → Atomizer ON")
        
        elif humidity >= HUMIDITY_THRESHOLD_OFF and current_state:
            # Humidity rose above 75%, turn off humidifier
            set_relay(port, False)
            logger.info(f"Humidity {humidity:.1f}% >= {HUMIDITY_THRESHOLD_OFF}% → Atomizer OFF")
        
        elif 60.0 <= humidity < 75.0:
            # In optimal range, maintain current state
            pass
    except Exception as e:
        logger.error(f"Error in humidity control: {e}")


@app.route('/')
def index():
    """Serve the main dashboard page."""
    return render_template('dashboard.html')


@app.route('/api/sensor/<int:sensor_id>', methods=['GET'])
def get_sensor(sensor_id):
    """
    Get current reading for a specific sensor with all 8 parameters.
    
    Args:
        sensor_id: Sensor ID (1-4)
    
    Returns:
        JSON with sensor data or error message
    """
    if not modbus_reader:
        return jsonify({'error': 'Modbus reader not initialized'}), 503
    
    if sensor_id not in range(1, 5):
        return jsonify({'error': 'Invalid sensor ID. Must be 1-4'}), 400
    
    try:
        data = modbus_reader.read_sensor(sensor_id)
        result = data.to_dict()
        result['timestamp'] = datetime.now().isoformat()
        return jsonify(result), 200
    except Exception as e:
        logger.error(f"Error reading sensor {sensor_id}: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/sensors', methods=['GET'])
def get_all_sensors():
    """
    Get current readings for all 4 sensors with all 8 parameters each.
    Automatically controls humidifier relay based on humidity levels.
    
    Returns:
        JSON with all sensor data and relay states
    """
    if not modbus_reader:
        return jsonify({'error': 'Modbus reader not initialized'}), 503
    
    try:
        all_sensors = modbus_reader.read_all_sensors()
        results = {}
        timestamp = datetime.now().isoformat()
        
        for sensor_id, data in all_sensors.items():
            result = data.to_dict()
            result['timestamp'] = timestamp
            results[str(sensor_id)] = result
            
            # Automatic humidity-based relay control for Port 1 (atomizer)
            if data.is_valid and data.humidity is not None:
                control_humidifier_based_on_humidity(data.humidity, port=1)
                # Add relay state to sensor data for dashboard
                result['humidifier'] = {'active': relay_states[1]['active']}
        
        # Add relay status to response
        results['_relays'] = {
            '1': {'active': relay_states[1]['active'], 'label': 'Atomizer/Humidifier'},
            '2': {'active': relay_states[2]['active'], 'label': 'Reserved'}
        }
        
        return jsonify(results), 200
    except Exception as e:
        logger.error(f"Error reading all sensors: {e}")
        return jsonify({'error': str(e)}), 500


@app.route('/api/status', methods=['GET'])
def get_status():
    """
    Get system status and connection information.
    
    Returns:
        JSON with status information including relay and humidity control settings
    """
    status = {
        'timestamp': datetime.now().isoformat(),
        'modbus_connected': modbus_reader is not None and modbus_reader.client is not None,
        'modbus_port': MODBUS_PORT,
        'modbus_baudrate': MODBUS_BAUDRATE,
        'sensors': [1, 2, 3, 4],
        'parameters_per_sensor': 8,
        'parameters': ['nitrogen', 'phosphorus', 'potassium', 'ph', 'ec', 'temperature', 'humidity'],
        'relay_control': {
            'enabled': True,
            'port_1': {
                'name': 'Atomizer/Humidifier',
                'humidity_threshold_on': HUMIDITY_THRESHOLD_ON,
                'humidity_threshold_off': HUMIDITY_THRESHOLD_OFF,
                'current_state': relay_states[1]['active']
            },
            'port_2': {
                'name': 'Reserved',
                'current_state': relay_states[2]['active']
            }
        }
    }
    return jsonify(status), 200


@app.route('/api/health', methods=['GET'])
def health_check():
    """Simple health check endpoint."""
    if modbus_reader and modbus_reader.client and modbus_reader.client.is_socket_open():
        return jsonify({'status': 'healthy'}), 200
    return jsonify({'status': 'unhealthy'}), 503


@app.errorhandler(404)
def not_found(error):
    """Handle 404 errors."""
    return jsonify({'error': 'Endpoint not found'}), 404


@app.errorhandler(500)
def internal_error(error):
    """Handle 500 errors."""
    logger.error(f"Internal server error: {error}")
    return jsonify({'error': 'Internal server error'}), 500


if __name__ == '__main__':
    # Ensure log directory exists
    os.makedirs('/var/log/soil-monitor', exist_ok=True)
    
    # Initialize Modbus
    if not init_modbus():
        logger.warning("Starting Flask server without Modbus connection")
    
    # Run Flask app (listen on both IPv4 and IPv6)
    try:
        app.run(host='::', port=5000, debug=False, threaded=True)
    except KeyboardInterrupt:
        logger.info("Shutting down...")
    finally:
        if modbus_reader:
            modbus_reader.disconnect()

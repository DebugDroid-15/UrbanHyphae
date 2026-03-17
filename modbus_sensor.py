"""
Modbus RTU sensor reader for NPK 7-Parameter soil sensors on Raspberry Pi.
Reads: Nitrogen, Phosphorus, Potassium, Moisture, pH, EC, Temperature
Handles communication with 4 sensors on RS-485 bus.
Includes calibration using linear regression (y = mx + b)
"""

import logging
import time
import struct
from typing import Dict, Optional
from pymodbus.client import ModbusSerialClient as ModbusClient
from pymodbus.exceptions import ModbusException

# Import calibration configuration
try:
    from calibration_config import apply_calibration
except ImportError:
    # Fallback if calibration config not available
    def apply_calibration(sensor_id, parameter, raw_value):
        return raw_value  # No calibration if config not found

logger = logging.getLogger(__name__)

try:
    import RPi.GPIO as GPIO
    GPIO_AVAILABLE = True
except (ImportError, RuntimeError):
    GPIO_AVAILABLE = False


class SensorData:
    """Container for 8-parameter sensor readings with calibration."""
    
    def __init__(self, sensor_id: int):
        self.sensor_id = sensor_id
        # Calibrated values (actual readings after correction)
        self.nitrogen: Optional[float] = None
        self.phosphorus: Optional[float] = None
        self.potassium: Optional[float] = None
        self.ph: Optional[float] = None
        self.ec: Optional[float] = None
        self.temperature: Optional[float] = None
        self.humidity: Optional[float] = None
        # Raw values (before calibration)
        self.nitrogen_raw: Optional[float] = None
        self.phosphorus_raw: Optional[float] = None
        self.potassium_raw: Optional[float] = None
        self.ph_raw: Optional[float] = None
        self.ec_raw: Optional[float] = None
        self.temperature_raw: Optional[float] = None
        # Metadata
        self.timestamp: Optional[str] = None
        self.is_valid: bool = False
        self.error: Optional[str] = None
    
    def to_dict(self) -> Dict:
        """Convert to dictionary for JSON serialization."""
        return {
            'sensor_id': self.sensor_id,
            'nitrogen': self.nitrogen,
            'phosphorus': self.phosphorus,
            'potassium': self.potassium,
            'ph': self.ph,
            'ec': self.ec,
            'temperature': self.temperature,
            'humidity': self.humidity,
            'timestamp': self.timestamp,
            'is_valid': self.is_valid,
            'error': self.error
        }
    
    def to_dict_with_raw(self) -> Dict:
        """Convert to dictionary including raw values (for diagnostics)."""
        data = self.to_dict()
        data['_raw'] = {
            'nitrogen': self.nitrogen_raw,
            'phosphorus': self.phosphorus_raw,
            'potassium': self.potassium_raw,
            'ph': self.ph_raw,
            'ec': self.ec_raw,
            'temperature': self.temperature_raw,
        }
        return data


class ModbusNPKReader:
    """
    Reads NPK 8-parameter soil sensor data via Modbus RTU over RS-485.
    
    Reads:
    - Nitrogen (N) in mg/kg
    - Phosphorus (P) in mg/kg
    - Potassium (K) in mg/kg
    - Soil pH (0-14)
    - Electrical Conductivity (EC) in mS/cm
    - Temperature in °C
    - Humidity in %
    """
    
    # Modbus holding register addresses (NPK sensor layout)
    # Read from address 4, 8 consecutive 16-bit registers
    REGISTER_START = 4              # Start reading from register 4
    REGISTER_COUNT = 8              # Read 8 registers total
    # Register layout at address 4:
    # reg[0-1]: not used
    # reg[2]: Nitrogen * 10
    # reg[3]: Phosphorus * 10
    # reg[4]: Potassium * 10
    # reg[5]: pH * 100
    # reg[6]: EC * 100
    # reg[7]: Temperature * 100
    
    def __init__(self, port: str = '/dev/ttyAMA0', baudrate: int = 9600, 
                 gpio_de_re: Optional[int] = 24, timeout: float = 1.0):
        """
        Initialize Modbus RTU reader.
        
        Args:
            port: Serial port for RS-485
            baudrate: Modbus RTU speed (typically 9600)
            gpio_de_re: GPIO pin for DE/RE control (set to None to disable)
            timeout: Read timeout in seconds
        """
        self.port = port
        self.baudrate = baudrate
        self.gpio_de_re = gpio_de_re
        self.timeout = timeout
        self.client: Optional[ModbusClient] = None
        self._gpio_available = False
        
        if gpio_de_re and GPIO_AVAILABLE:
            self._setup_gpio()
    
    def _setup_gpio(self):
        """Setup GPIO for DE/RE pin control."""
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(self.gpio_de_re, GPIO.OUT)
            GPIO.output(self.gpio_de_re, GPIO.LOW)  # Receiver mode by default
            self._gpio_available = True
            logger.info(f"GPIO {self.gpio_de_re} configured for DE/RE control")
        except Exception as e:
            logger.warning(f"GPIO setup failed: {e}")
            self._gpio_available = False
    
    def _set_tx_mode(self):
        """Enable transmit mode (DE=HIGH)."""
        if self._gpio_available:
            GPIO.output(self.gpio_de_re, GPIO.HIGH)
            time.sleep(0.01)
    
    def _set_rx_mode(self):
        """Enable receive mode (RE=LOW)."""
        if self._gpio_available:
            time.sleep(0.01)
            GPIO.output(self.gpio_de_re, GPIO.LOW)
    
    def connect(self) -> bool:
        """Establish Modbus RTU connection."""
        try:
            self.client = ModbusClient(
                port=self.port,
                baudrate=self.baudrate,
                timeout=self.timeout
            )
            if self.client.connect():
                logger.info(f"Connected to Modbus RTU on {self.port} @ {self.baudrate} baud")
                return True
            else:
                logger.error("Failed to connect to Modbus RTU")
                return False
        except Exception as e:
            logger.error(f"Connection error: {e}")
            return False
    
    def disconnect(self):
        """Close Modbus connection and cleanup GPIO."""
        if self.client:
            self.client.close()
            logger.info("Disconnected from Modbus RTU")
        
        if self._gpio_available:
            try:
                GPIO.cleanup()
            except Exception as e:
                logger.warning(f"GPIO cleanup error: {e}")
    
    @staticmethod
    def _parse_float32(high_register: int, low_register: int) -> Optional[float]:
        """
        Parse two 16-bit registers into a 32-bit IEEE 754 float.
        
        Args:
            high_register: High word (16-bit)
            low_register: Low word (16-bit)
            
        Returns:
            Float value or None if parsing fails
        """
        try:
            # Combine registers into 32-bit value
            combined = (high_register << 16) | low_register
            # Unpack as IEEE 754 float
            float_value = struct.unpack('f', struct.pack('I', combined))[0]
            return float_value
        except (struct.error, ValueError):
            return None
    
    def read_sensor(self, sensor_id: int, retries: int = 3) -> SensorData:
        """
        Read all parameters from a single sensor at address 4.
        Only Sensor 1 is connected. Sensors 2-4 return empty data.
        
        Args:
            sensor_id: Modbus ID (1 for the connected sensor, 2-4 for disconnected)
            retries: Number of retry attempts on failure
            
        Returns:
            SensorData object with readings
        """
        data = SensorData(sensor_id)
        
        # Sensors 2-4 are not connected - return empty data
        if sensor_id > 1:
            data.error = f"Sensor {sensor_id} not connected"
            data.is_valid = False
            return data
        
        if not self.client or not self.client.is_socket_open():
            data.error = "Not connected to Modbus RTU"
            logger.error(f"Sensor {sensor_id}: {data.error}")
            return data
        
        for attempt in range(retries):
            try:
                self._set_tx_mode()
                
                # Read 8 registers starting at address 4
                # reg[0-1]: unused
                # reg[2]: Nitrogen * 10
                # reg[3]: Phosphorus * 10
                # reg[4]: Potassium * 10
                # reg[5]: pH * 100
                # reg[6]: EC * 100
                # reg[7]: Temperature * 100
                result = self.client.read_holding_registers(
                    address=self.REGISTER_START,
                    count=self.REGISTER_COUNT,
                    device_id=sensor_id
                )
                
                self._set_rx_mode()
                
                if isinstance(result, Exception) or result.isError():
                    logger.debug(f"Sensor {sensor_id} read error (attempt {attempt+1}): {result}")
                    time.sleep(0.1)
                    continue
                
                # Parse parameters from 8 registers (raw values)
                regs = result.registers
                
                # Store raw values
                data.nitrogen_raw = regs[2] / 10.0 if regs[2] is not None else None
                data.phosphorus_raw = regs[3] / 10.0 if regs[3] is not None else None
                data.potassium_raw = regs[4] / 10.0 if regs[4] is not None else None
                data.ph_raw = regs[5] / 100.0 if regs[5] is not None else None
                data.ec_raw = regs[6] / 100.0 if regs[6] is not None else None
                data.temperature_raw = regs[7] / 100.0 if regs[7] is not None else None
                
                # Apply calibration to get corrected values
                data.nitrogen = apply_calibration(sensor_id, 'nitrogen', data.nitrogen_raw) if data.nitrogen_raw is not None else None
                data.phosphorus = apply_calibration(sensor_id, 'phosphorus', data.phosphorus_raw) if data.phosphorus_raw is not None else None
                data.potassium = apply_calibration(sensor_id, 'potassium', data.potassium_raw) if data.potassium_raw is not None else None
                data.ph = apply_calibration(sensor_id, 'ph', data.ph_raw) if data.ph_raw is not None else None
                data.ec = apply_calibration(sensor_id, 'ec', data.ec_raw) if data.ec_raw is not None else None
                data.temperature = apply_calibration(sensor_id, 'temperature', data.temperature_raw) if data.temperature_raw is not None else None
                
                # No humidity parameter in this sensor model
                data.humidity = None
                
                data.is_valid = True
                logger.info(f"Sensor {sensor_id} (RAW→CALIBRATED): "
                           f"N={data.nitrogen_raw:.1f}→{data.nitrogen:.1f} "
                           f"P={data.phosphorus_raw:.1f}→{data.phosphorus:.1f} "
                           f"K={data.potassium_raw:.1f}→{data.potassium:.1f} "
                           f"pH={data.ph_raw:.2f}→{data.ph:.2f} "
                           f"EC={data.ec_raw:.2f}→{data.ec:.2f} "
                           f"T={data.temperature_raw:.1f}→{data.temperature:.1f}°C")
                return data
                
                logger.debug(f"Sensor {sensor_id} Modbus exception (attempt {attempt+1}): {str(e)}")
                time.sleep(0.1)
            except Exception as e:
                logger.debug(f"Sensor {sensor_id} read error (attempt {attempt+1}): {str(e)}")
                time.sleep(0.1)
        
        # All retries failed
        data.error = f"Failed to read after {retries} attempts"
        logger.error(f"Sensor {sensor_id}: {data.error}")
        return data
    
    def read_all_sensors(self) -> Dict[int, SensorData]:
        """
        Read data from all 4 sensors sequentially.
        Sensor 1 is connected and returns real data.
        Sensors 2-4 are disconnected and return empty data with error message.
        
        Returns:
            Dictionary mapping sensor_id to SensorData
        """
        results = {}
        for sensor_id in range(1, 5):
            results[sensor_id] = self.read_sensor(sensor_id)
        return results


def initialize_logger(log_file: Optional[str] = None, level: int = logging.INFO):
    """Setup logging configuration."""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    if log_file:
        file_handler = logging.FileHandler(log_file)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    logger.setLevel(level)


if __name__ == '__main__':
    # Test connection (requires actual hardware)
    initialize_logger()
    
    reader = ModbusNPKReader(port='/dev/serial0')
    if reader.connect():
        sensors_data = reader.read_all_sensors()
        for sensor_id, data in sensors_data.items():
            print(f"\nSensor {sensor_id}:")
            print(f"  N: {data.nitrogen} mg/kg")
            print(f"  P: {data.phosphorus} mg/kg")
            print(f"  K: {data.potassium} mg/kg")
            print(f"  pH: {data.ph}")
            print(f"  EC: {data.ec} mS/cm")
            print(f"  Temperature: {data.temperature}°C")
            print(f"  Humidity: {data.humidity}%")
            if not data.is_valid:
                print(f"  Error: {data.error}")
        reader.disconnect()

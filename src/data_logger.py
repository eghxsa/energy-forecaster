import os
import time
import csv
import logging
from datetime import datetime, timedelta
from hive_session import get_hive_session
from weather import get_weather
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
thermostat_id = os.getenv("THERMOSTAT_ID")

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data/logger.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


# Fetch Hive and weather data, write to CSV
def log_data():
    session = get_hive_session()
    if not session:
        logger.error("Failed to get Hive session")
        return
    
    try:
        # Get heating devices
        heating_devices = session.deviceList.get("climate", [])
        
        if not heating_devices:
            logger.warning("No heating devices found")
            return
        
        device = heating_devices[0]
        
        # Get temperature data from heating device
        temp = session.heating.getCurrentTemperature(device)
        target = session.heating.getTargetTemperature(device)
        heating = session.heating.getCurrentOperation(device)
        
        # Get battery and signal from thermostat device
        thermostat = session.data.devices.get(thermostat_id, {})
        props = thermostat.get("props", {})
        battery = props.get("battery")
        signal = props.get("signal")
        online = props.get("online", False)

        # Get weather data
        weather = get_weather()
        outside_temp = weather["outside_temp"]
        humidity = weather["humidity"]
        wind_speed = weather["wind_speed"]
        weather_desc = weather["weather_description"]
        
        # Write to CSV
        with open("data/thermostat_log.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                temp, target, heating, battery, signal, online,
                outside_temp, humidity, wind_speed, weather_desc
            ])
        
        logger.info(f"Logged: {temp}°C | Target: {target}°C | Outside: {outside_temp}°C | Heating: {heating}")
        
    except Exception as e:
        logger.error(f"Error logging data: {e}")

if __name__ == "__main__":
    # Ensure data directory exists
    os.makedirs("data", exist_ok=True)

    # Create CSV with headers if it does not exist
    if not os.path.exists("data/thermostat_log.csv"):
        with open("data/thermostat_log.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "temperature", "target_temperature",
                "heating", "battery", "signal", "online",
                "outside_temp", "humidity", "wind_speed", "weather_desc"
            ])

    # Run once (cron will handle scheduling)
    log_data()
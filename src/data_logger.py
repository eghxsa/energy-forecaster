import os
import time
import csv
from datetime import datetime, timedelta
from hive_session import get_hive_session
from weather import get_weather
from dotenv import load_dotenv

load_dotenv()
thermostat_id = os.getenv("THERMOSTAT_ID")

def log_data():
    """Fetch Hive and weather data, write to CSV"""
    session = get_hive_session()
    
    if not session:
        return
    
    try:
        # Get heating devices
        heating_devices = session.deviceList.get("climate", [])
        
        if not heating_devices:
            print("No heating devices found")
            return
        
        device = heating_devices[0]
        
        # Get temperature
        temp = session.heating.getCurrentTemperature(device)
        target = session.heating.getTargetTemperature(device)
        heating = session.heating.getCurrentOperation(device)
        
        # Get battery and signal
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
        
        print(f"Logged: {temp}°C | Target: {target}°C | Outside: {outside_temp}°C | Heating: {heating}")
        
    except Exception as e:
        print(f"Error logging data: {e}")

def main():
    print("Starting logger...")
    print("   Press Ctrl+C to stop\n")
    
    os.makedirs("data", exist_ok=True)
    
    if not os.path.exists("data/thermostat_log.csv"):
        with open("data/thermostat_log.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp", "temperature", "target_temperature",
                "heating", "battery", "signal", "online",
                "outside_temp", "humidity", "wind_speed", "weather_desc"
            ])
    
    while True:
        try:
            log_data()
            print(f"Next poll in 5 minutes...\n")
            time.sleep(300)
        except KeyboardInterrupt:
            print("\nLogger stopped.")
            break
        except Exception as e:
            print(f"Error in main loop: {e}")
            time.sleep(60)

if __name__ == "__main__":
    main()
import os
import time
import csv
from datetime import datetime, timedelta
from dotenv import load_dotenv
from hive_client import get_hive_session

# Load credentials from .env file
load_dotenv()
thermostat_id = os.getenv("THERMOSTAT_ID")

# Fetch thermostat data and append to CSV
def log_data():
    hive = get_hive_session()

    try:
        hive.getDevices("No_ID")

        for device in hive.data.devices.values():
            if device.get("id") != thermostat_id:
                continue
            
            props = device.get("props", {})
            state = device.get("state", {})

            temp = props.get("temperature") or state.get("temperature")
            target = props.get("targetTemperature") or state.get("targetTemperature")
            heating = props.get("heating") or state.get("heating")
            battery = props.get("battery")
            signal = props.get("signal")
            online = props.get("online", False)

            with open("data/thermostat_log.csv", "a", newline="") as f:
                writer = csv.writer(f)
                writer.writerow([
                    datetime.now().isoformat(),
                    temp, target, heating, battery, signal, online])

            print(f"Logged: {temp}°C | Target: {target}°C | Heating: {heating}")
            break

    except Exception as e:
        print(f"Error logging data: {e}")

def main():
    print("Starting thermostat data logger...")
    print("Press Control+C to stop\n")

    os.makedirs("data", exist_ok=True)

    if not os.path.exists("data/thermostat_log.csv"):
        with open("data/thermostat_log.csv", "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "temperature", "target_temperature",
            "heating", "battery", "signal", "online"])

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


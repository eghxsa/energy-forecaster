import os
import time
import csv
from datetime import datetime, timedelta
from pyhiveapi import Auth, Hive
from dotenv import load_dotenv

load_dotenv()
username = os.getenv("HIVE_EMAIL")
password = os.getenv("HIVE_PASSWORD")

# Device credentials from registration
DEVICE_GROUP_KEY = os.getenv("DEVICE_GROUP_KEY")
DEVICE_KEY = os.getenv("DEVICE_KEY")
DEVICE_PASSWORD = os.getenv("DEVICE_PASSWORD")

def get_hive_session_device():
    """Get authenticated Hive session using device credentials."""
    # Create Auth object with device credentials
    auth = Auth(username=username, password=password)
    auth.device_group_key = DEVICE_GROUP_KEY
    auth.device_key = DEVICE_KEY
    auth.device_password = DEVICE_PASSWORD
    
    # Login with device authentication
    try:
        # Try device login
        login_result = auth.device_login()
        print("Device login successful")
    except Exception as e:
        print(f"Device login failed: {e}")
        return None
    
    # Extract tokens
    tokens = login_result["AuthenticationResult"]
    access_token = tokens["AccessToken"]
    
    # Create Hive session with tokens
    session = Hive(username=username, password=password)
    session.tokens.tokenData = {
        "token": tokens["IdToken"],
        "accessToken": access_token,
        "refreshToken": tokens["RefreshToken"]
    }
    session.tokens.tokenCreated = datetime.now()
    session.tokens.tokenExpiry = timedelta(seconds=tokens.get("ExpiresIn", 3600))
    
    # Set access token on session auth
    session.auth.access_token = access_token
    
    # Start the session
    session.startSession()
    
    return session

def log_data():
    """Fetch thermostat data using device authentication."""
    session = get_hive_session_device()
    
    if not session:
        return
    
    try:
        # Get heating devices
        heating_devices = session.deviceList.get("climate", [])
        
        if not heating_devices:
            print("No heating devices found")
            print(f"Available device lists: {list(session.deviceList.keys())}")
            return
        
        device = heating_devices[0]
        print(f"Found device: {device.get('hiveName', 'Unknown')}")
        
        # Get temperature
        temp = session.heating.getCurrentTemperature(device)
        target = session.heating.getTargetTemperature(device)
        heating = session.heating.getCurrentOperation(device)
        
        # Get battery and signal
        props = device.get("props", {})
        battery = props.get("battery")
        signal = props.get("signal")
        online = props.get("online", False)
        
        # Write to CSV
        with open("data/thermostat_log.csv", "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                datetime.now().isoformat(),
                temp, target, heating, battery, signal, online
            ])
        
        print(f"Logged: {temp}°C | Target: {target}°C | Heating: {heating}")
        
    except Exception as e:
        print(f"Error logging data: {e}")

def main():
    print("Starting thermostat data logger (device auth)...")
    print("   Press Ctrl+C to stop\n")
    
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
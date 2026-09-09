import os
import asyncio
from datetime import datetime, timedelta
from pyhiveapi import Auth, Hive
from dotenv import load_dotenv

# Load credentials from .env file
load_dotenv()
username = os.getenv("HIVE_EMAIL")
password = os.getenv("HIVE_PASSWORD")

def get_hive_session():
    # Create session and manually set tokens
    # Login
    auth = Auth(username, password)
    login_result = auth.login()
    tokens = login_result["AuthenticationResult"]

    hive = Hive(username, password)
    hive.tokens.tokenData = {
        "token": tokens["IdToken"],
        "accessToken": tokens["AccessToken"],
        "refreshToken": tokens["RefreshToken"]
    }
    hive.tokens.tokenCreated = datetime.now()
    hive.tokens.tokenExpiry = timedelta(seconds=tokens["ExpiresIn"])
    return hive

def main():
    # Fetch and display devices
    hive = get_hive_session()
    hive.getDevices("No_ID")
    print("✅ Devices fetched successfully!\n")
    for device in hive.data.devices.values():
        print(device)

if __name__ == "__main__":
    main()
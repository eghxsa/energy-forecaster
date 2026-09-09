import os
import asyncio
from datetime import datetime, timedelta
from apyhiveapi import Auth, Hive, SMS_REQUIRED
from dotenv import load_dotenv

load_dotenv()
username = os.getenv("HIVE_EMAIL")
password = os.getenv("HIVE_PASSWORD")

async def register_device():
    """Register a device and get device credentials."""
    # 1. Login with 2FA
    auth = Auth(username=username, password=password)
    login_result = await auth.login()
    
    if login_result.get("ChallengeName") == SMS_REQUIRED:
        code = input("Enter 2FA code: ")
        login_result = await auth.sms_2fa(code, login_result)
    
    # 2. Extract tokens
    tokens = login_result["AuthenticationResult"]
    access_token = tokens["AccessToken"]
    
    # 3. Create session and set tokens
    session = Hive(username=username, password=password)
    session.tokens.tokenData = {
        "token": tokens["IdToken"],
        "accessToken": access_token,
        "refreshToken": tokens["RefreshToken"]
    }
    session.tokens.tokenCreated = datetime.now()
    session.tokens.tokenExpiry = timedelta(seconds=tokens.get("ExpiresIn", 3600))
    
    # 4. Set the access token on the auth object
    session.auth.access_token = access_token
    
    # 5. Set the device key and device group key from the login
    session.auth.device_group_key = os.getenv("DEVICE_GROUP_KEY")
    session.auth.device_key = os.getenv("DEVICE_KEY")
    
    # 6. Start session
    await session.startSession({"tokens": tokens})
    
    # 7. Get devices
    await session.getDevices("No_ID")
    print("Devices fetched successfully")
    
    # 8. Register the device
    try:
        print("\nRegistering device...")
        await session.auth.device_registration('my_laptop')
        print("Device registration successful!")
    except Exception as e:
        print(f"Device registration failed: {e}")
    
    # 9. Get device data (await the coroutine)
    device_data = await session.auth.get_device_data()
    
    print("\nDevice registration completed!")
    print("\nSave these credentials for future use:")
    print(f"device_group_key = '{device_data[0]}'")
    print(f"device_key = '{device_data[1]}'")
    print(f"device_password = '{device_data[2]}'")
    
    return device_data

if __name__ == "__main__":
    asyncio.run(register_device())
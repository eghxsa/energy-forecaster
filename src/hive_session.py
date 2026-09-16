import os
from datetime import datetime, timedelta
from pyhiveapi import Auth, Hive
from dotenv import load_dotenv

# Load credentials
load_dotenv()
username = os.getenv("HIVE_EMAIL")
password = os.getenv("HIVE_PASSWORD")
DEVICE_GROUP_KEY = os.getenv("DEVICE_GROUP_KEY")
DEVICE_KEY = os.getenv("DEVICE_KEY")
DEVICE_PASSWORD = os.getenv("DEVICE_PASSWORD")

def get_hive_session():
    """Get authenticated Hive session using device credentials"""
    auth = Auth(username=username, password=password)
    auth.device_group_key = DEVICE_GROUP_KEY
    auth.device_key = DEVICE_KEY
    auth.device_password = DEVICE_PASSWORD

    login_result = auth.device_login()
    tokens = login_result["AuthenticationResult"]

    session = Hive(username=username, password=password)
    session.tokens.tokenData = {
        "token": tokens["IdToken"],
        "accessToken": tokens["AccessToken"],
        "refreshToken": tokens["RefreshToken"]
    }
    session.tokens.tokenCreated = datetime.now()
    session.tokens.tokenExpiry = timedelta(seconds=tokens.get("ExpiresIn"))

    session.auth.access_token = tokens["AccessToken"]
    session.startSession()

    return session
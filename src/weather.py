import os
import requests
from dotenv import load_dotenv

load_dotenv()
lat = os.getenv("LATITUDE")
lon = os.getenv("LONGITUDE")
api_key = os.getenv("OPENWEATHER_API_KEY")

def get_weather():
    """Fetch current weather data"""
    url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={api_key}&units=metric"

    response = requests.get(url, timeout=10)
    data = response.json()
    return {
        "outside_temp": data["main"]["temp"],
        "humidity": data["main"]["humidity"],
        "wind_speed": data["wind"]["speed"],
        "weather_description": data["weather"][0]["main"]
    }

if __name__ == "__main__":
    print(get_weather())
# Home Climate Forecaster

An end-to-end data pipeline that collects real-time data from a Hive smart thermostat + OpenWeatherMap API, and uses machine learning to forecast indoor climate conditions.

## Features
- Authenticates with the Hive API
- Logs thermostat data (temperature, heating status, battery level)
- Fetches outside weather data (temperature, humidity, wind speed) fro OpenWeatherMap
- Saves combined data to CSV for analysis
- Deployed to Oracle Cloud with automated cron scheduling (every 5 minutes)
- (WIP) Machine learning models to forecast indoor temperature

## Setup
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
`venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
3. Install dependencies: `pip install -r requirements.txt`
4. Register your Hive device (one-time)
`python src/register_device.py`
5. Create a `.env` file 
# Hive credentials
    HIVE_EMAIL
    HIVE_PASSWORD
    DEVICE_GROUP_KEY
    DEVICE_KEY
    DEVICE_PASSWORD
    THERMOSTAT_ID

# Weather API credentials
    LATITUDE
    LONGITUDE
    OPENWEATHER_API_KEY
6. Run `python src/hive_client.py` to identify Thermostat ID and update `.env` to include THERMOSTAT_ID
7. Run: `python src/data_logger.py`

## Technologies
- Python, pyhive-integration
- OpenWeatherMap API
- Oracle Cloud (VM + cron)
- pandas, scikit-learn, XGBoost (for modelling)

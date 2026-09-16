# Hive Home Energy Consumption Forecaster

An end-to-end data pipeline that collects energy data from a Hive smart thermostat and uses machine learning to forecast energy usage.

## Features
- Authenticates with the Hive API
- Logs thermostat data (temperature, heating status, battery level)
- Saves data to CSV for analysis
- (WIP) Machine learning models to predict energy usage

## Setup
1. Clone the repository
2. Create a virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`
5. Create a `.env` file with your Hive credentials:
    HIVE_EMAIL=your_email@example.com
    HIVE_PASSWORD=your_password
6. Run `python src/hive_client.py` to identify Thermostat ID and update `.env` to include THERMOSTAT_ID
7. Run: `python src/data_logger.py`

## Technologies
- Python, pyhiveapi
- pandas, scikit-learn, XGBoost (for modelling)

## Project Status
- [x] Data collection pipeline
- [ ] Data analysis
- [ ] Predictive modelling

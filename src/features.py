# Feature engineering for Home Climate Forecaster
import pandas as pd
import numpy as np

base_temp = 15.5 # HDD baseline (°C)

def add_segment(df, ts_col="timestamp"):
    df = df.copy()
    df = df.sort_values(ts_col).reset_index(drop=True)
    ts = pd.to_datetime(df[ts_col])
    
    # Calculate the time difference between rows in minutes
    deltas = ts.diff().dt.total_seconds() / 60
    
    # A new segment starts whenever the gap is greater than 60 minutes
    # (This catches the 4-day gap, the 14-day gap, and any other major outages)
    is_new_segment = (deltas > 60) | (deltas.isna())
    
    # Cumulatively sum the booleans to create segment IDs (0, 1, 2, 3...)
    df["segment"] = is_new_segment.cumsum()
    
    return df

def add_time_features(df, ts_col="timestamp"):
    df = df.copy()
    ts = pd.to_datetime(df[ts_col])
    df["hour"] = ts.dt.hour
    df["day_of_week"] = ts.dt.dayofweek
    df["month"] = ts.dt.month
    
    # Cyclical encodings 
    df["hour_sin"] = np.sin(2*np.pi*df["hour"]/24)
    df["hour_cos"] = np.cos(2*np.pi*df["hour"]/24)
    df["dow_sin"] = np.sin(2*np.pi*df["day_of_week"]/7)
    df["dow_cos"] = np.cos(2*np.pi*df["day_of_week"]/7)
    return df

def add_lag_features(df, col="temperature", lags=(1, 3, 12, 24)):
    # Lags in 5-min steps: 1=5min, 3=15min, 12=1h, 24=2h
    # Gap-safe: group by segment so lags never bridge the 14-day outage
    df = df.copy()
    for lag in lags:
        df[f"{col}_lag_{lag}"] = df.groupby("segment")[col].shift(lag)
    return df

def add_rolling_features(df, col="temperature", windows=(3,12,24)):
    # Rolling stats using only past data
    df = df.copy()
    for w in windows:
        df[f"{col}_roll_mean_{w}"] = (
            df.groupby("segment")[col].transform(lambda s: s.shift(1).rolling(w).mean())
            )
        df[f"{col}_roll_std_{w}"] = (
            df.groupby("segment")[col].transform(lambda s: s.shift(1).rolling(w).std())
        )
    return df

def add_physics_features(df):
    df = df.copy()
    df["temp_diff"] = df["temperature"] - df["outside_temp"]
    df["hdd"] = (base_temp - df["outside_temp"]).clip(lower=0)
    return df

def add_heating_and_setpoint(df):
    df = df.copy()
    df["heating_on"] = (
        df["heating"].astype(str).str.strip().str.lower().eq("true").astype(int)
    )
    df["setpoint_active"] = (df["target_temperature"] > 10).astype(int)
    return df

def build_features(df, drop_na=True):
    df = df.copy()
    df = add_segment(df)
    df = add_time_features(df)
    df = add_lag_features(df)
    df = add_rolling_features(df)
    df = add_physics_features(df)
    df = add_heating_and_setpoint(df)
    if drop_na:
        df = df.dropna().reset_index(drop=True)
    return df

FEATURE_COLS = [
    "outside_temp", "humidity", "wind_speed",
    "hour_sin", "hour_cos", "dow_sin", "dow_cos", "month",
    "heating_on", "setpoint_active",
    "temperature_lag_1", "temperature_lag_3", "temperature_lag_12", "temperature_lag_24",
    "temperature_roll_mean_3", "temperature_roll_mean_12",
    "temperature_roll_mean_24", "temperature_roll_std_12",
    "temp_diff", "hdd"
]

TARGET_COL = "temperature"
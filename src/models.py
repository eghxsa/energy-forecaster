# Model training and comparison for Home Climate Forecaster.
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from xgboost import XGBRegressor


def segment_split(df):
    # Train on autumn (segments 1 and 2), test on early winter (segment 3).
    train = df[df["segment"].isin([1, 2])].copy()
    test  = df[df["segment"] == 3].copy()
    return train, test


def evaluate(y_true, y_pred, name):
    return {
        "model": name,
        "RMSE": float(np.sqrt(mean_squared_error(y_true, y_pred))),
        "MAE": float(mean_absolute_error(y_true, y_pred)),
        "R2": float(r2_score(y_true, y_pred)),
    }


def get_models():
    return {
        "LinearRegression": LinearRegression(),
        "RandomForest": RandomForestRegressor(
            n_estimators=300, min_samples_leaf=2, n_jobs=-1, random_state=42,
        ),
        "XGBoost": XGBRegressor(
            n_estimators=400, learning_rate=0.05, max_depth=6,
            subsample=0.9, colsample_bytree=0.9,
            random_state=42, n_jobs=-1, verbosity=0,
        ),
    }


def persistence_baseline(test_df, target_col="temperature", lag_col="temperature_lag_1"):
    """Naive baseline: predict next temp = previous temp. Must beat this."""
    return test_df[lag_col].values
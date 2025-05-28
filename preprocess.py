import pandas as pd
import numpy as np
import os
from config import DATA_FOLDER

# Function to load CSV files
def load_data(file):
    file_path = os.path.join(DATA_FOLDER, file)
    if not os.path.exists(file_path):
        print(f"⚠ File not found: {file_path}")
        return None
    return pd.read_csv(file_path)

# Function to process data and add features
def preprocess_data(df):
    df["timestamp"] = pd.to_datetime(df["timestamp"])
    df.set_index("timestamp", inplace=True)

    # Convert data types
    df = df.astype(float)

    # Calculate Moving Averages
    df["MA_10"] = df["close"].rolling(window=10).mean()
    df["MA_50"] = df["close"].rolling(window=50).mean()

    # Calculate RSI (Relative Strength Index)
    delta = df["close"].diff(1)
    gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
    rs = gain / loss
    df["RSI"] = 100 - (100 / (1 + rs))

    # Remove NaN values
    df.dropna(inplace=True)

    return df

# Load and process BTCUSDT data
df = load_data("BTCUSDT_prices.csv")

if df is not None:
    df = preprocess_data(df)
    print(df.head())

    # Save preprocessed data
    df.to_csv(os.path.join(DATA_FOLDER, "BTCUSDT_preprocessed.csv"))
    print("✅ Preprocessed data saved!")

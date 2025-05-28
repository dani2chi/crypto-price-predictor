import os
import yfinance as yf
import requests
import pandas as pd
import time
from datetime import datetime
from config import STOCKS, CRYPTOS, BINANCE_URL, DATA_FOLDER

# Ensure the data folder exists
if not os.path.exists(DATA_FOLDER):
    os.makedirs(DATA_FOLDER)

# Function to fetch stock data from Yahoo Finance
def fetch_stock_data():
    for stock in STOCKS:
        print(f"📈 Fetching stock data for {stock}...")

        try:
            # Download last 100 days of stock prices
            df = yf.download(stock, period="100d", interval="1d")

            if df.empty:
                print(f"⚠ No data found for {stock}. Skipping...")
                continue  # Skip this stock if no data

            # Save to CSV file
            filename = os.path.join(DATA_FOLDER, f"{stock}_prices.csv")
            df.to_csv(filename)

            print(f"✅ Saved {stock} data to {filename}")

        except Exception as e:
            print(f"❌ Error fetching stock data for {stock}: {e}")

# Function to fetch crypto data from Binance API
def fetch_crypto_data():
    for crypto in CRYPTOS:
        print(f"🪙 Fetching crypto data for {crypto}...")

        retries = 3  # Number of retries
        response = None

        for attempt in range(retries):
            try:
                response = requests.get(BINANCE_URL, params={"symbol": crypto, "interval": "1d", "limit": 100}, timeout=10)
                response.raise_for_status()  # Raise an error for bad response
                response = response.json()
                break  # Exit loop if successful

            except requests.exceptions.Timeout:
                print(f"⚠ Timeout on attempt {attempt + 1}/{retries} for {crypto}")
                time.sleep(5)  # Wait 5 seconds before retrying

            except requests.exceptions.RequestException as e:
                print(f"❌ Error fetching {crypto} data: {e}")
                return  # Stop if there's a critical request error

        if response is None:
            print(f"❌ Failed to fetch {crypto} after {retries} attempts.")
            return

        # Convert response to DataFrame
        columns = ["timestamp", "open", "high", "low", "close", "volume", "close_time", "quote_asset_volume", "trades", "taker_buy_base", "taker_buy_quote", "ignore"]
        df = pd.DataFrame(response, columns=columns)

        # Convert timestamp
        df["timestamp"] = pd.to_datetime(df["timestamp"], unit="ms")

        # Convert only numeric columns to float
        numeric_columns = ["open", "high", "low", "close", "volume"]
        df[numeric_columns] = df[numeric_columns].astype(float)

        # Keep only relevant columns
        df = df[["timestamp"] + numeric_columns]

        # Save to CSV
        filename = os.path.join(DATA_FOLDER, f"{crypto}_prices.csv")
        df.to_csv(filename, index=False)

        print(f"✅ Saved {crypto} data to {filename}")


# Run both functions to fetch stock & crypto data
if __name__ == "__main__":
    fetch_stock_data()
    fetch_crypto_data()

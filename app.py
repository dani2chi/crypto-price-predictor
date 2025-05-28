import streamlit as st
import requests
import pandas as pd
import plotly.graph_objects as go

# ✅ Alpha Vantage API for OHLC Data
ALPHA_VANTAGE_URL = "https://www.alphavantage.co/query"
ALPHA_VANTAGE_API_KEY = "00CW7K75N41619P7"  # 🔹 Replace this with your actual API key

# ✅ Set Prediction API URL (Replace with your deployed API URL)
API_URL = "https://crypto-price-predictor-production.up.railway.app/predict/"

# Function to fetch available cryptocurrencies dynamically
def get_supported_cryptos():
    available_cryptos = ["BTC", "ETH", "ADA", "SOL", "XRP", "DOGE"]  # BNB removed
    return available_cryptos


# Function to fetch crypto data from Alpha Vantage
def get_crypto_data(symbol="BTC", market="USD"):
    params = {
        "function": "DIGITAL_CURRENCY_DAILY",
        "symbol": symbol,
        "market": market,
        "apikey": ALPHA_VANTAGE_API_KEY
    }
    
    try:
        response = requests.get(ALPHA_VANTAGE_URL, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if "Time Series (Digital Currency Daily)" not in data:
            st.error("⚠ No data received from Alpha Vantage API")
            return None
        
        # Convert response to DataFrame
        df = pd.DataFrame.from_dict(data["Time Series (Digital Currency Daily)"], orient="index")
        df["timestamp"] = pd.to_datetime(df.index)
        df = df.sort_values("timestamp")

        # ✅ Correct column mappings based on API response
        expected_columns = {
            "1. open": "open",
            "2. high": "high",
            "3. low": "low",
            "4. close": "close",
            "5. volume": "volume"
        }

        # ✅ Rename columns correctly
        df = df.rename(columns=lambda col: expected_columns.get(col, col))

        # ✅ Ensure required columns exist before converting
        for col in ["open", "high", "low", "close", "volume"]:
            if col not in df:
                st.error(f"⚠ Missing column: {col} in API response")
                return None

        df["open"] = df["open"].astype(float)
        df["high"] = df["high"].astype(float)
        df["low"] = df["low"].astype(float)
        df["close"] = df["close"].astype(float)
        df["volume"] = df["volume"].astype(float)

        return df

    except requests.exceptions.Timeout:
        st.error("⚠ Alpha Vantage API request timed out")
        return None
    except requests.exceptions.RequestException as e:
        st.error(f"⚠ Alpha Vantage API Error: {e}")
        return None


# Streamlit UI
st.title("📈 Crypto Price Prediction & Live Charts")

# Sidebar for selecting cryptocurrency
crypto_symbol = st.sidebar.selectbox("Select Cryptocurrency", get_supported_cryptos())

# Fetch real-time data
df = get_crypto_data(crypto_symbol)

if df is not None:
    # ✅ Display latest price
    latest_price = df["close"].iloc[-1]
    st.metric(label=f"Latest {crypto_symbol} Price", value=f"${latest_price:,.2f}")

    # ✅ Plot interactive candlestick chart
    fig = go.Figure()
    fig.add_trace(go.Candlestick(
        x=df["timestamp"],
        open=df["open"],
        high=df["high"],
        low=df["low"],
        close=df["close"],
        name="Market Data"
    ))
    fig.update_layout(title=f"{crypto_symbol} Price Chart", xaxis_title="Date", yaxis_title="Price (USD)")
    st.plotly_chart(fig)

    # Compute Moving Averages
    df["MA_10"] = df["close"].rolling(window=10).mean()
    df["MA_50"] = df["close"].rolling(window=50).mean()

    # ✅ Allow user input for prediction
    st.subheader("Predict Future Price Movement")
    price_input = st.number_input("Latest Price", min_value=0.0, value=float(latest_price))
    volume = st.number_input("Volume", min_value=0.0, value=float(df["volume"].iloc[-1]))
    ma_10 = st.number_input("10-Day Moving Average", min_value=0.0, value=float(df["MA_10"].iloc[-1]))
    ma_50 = st.number_input("50-Day Moving Average", min_value=0.0, value=float(df["MA_50"].iloc[-1]))
    rsi = st.number_input("Relative Strength Index (RSI)", min_value=0.0, max_value=100.0, value=50.0)

    # ✅ Predict button with loading spinner
    if st.button("Predict Price Movement"):
        with st.spinner("🔮 Predicting..."):
            data = {
                "open": price_input,
                "high": price_input * 1.01,
                "low": price_input * 0.99,
                "close": price_input,
                "volume": volume,
                "MA_10": ma_10,
                "MA_50": ma_50,
                "RSI": rsi
            }
            response = requests.post(API_URL, json=data)
            if response.status_code == 200:
                result = response.json()

                # ✅ Color-coded prediction output
                if result['prediction'] == "Up":
                    st.success(f"📈 Prediction: **{result['prediction']}**")
                else:
                    st.error(f"📉 Prediction: **{result['prediction']}**")
            else:
                st.error("❌ Failed to get a prediction. Check API.")

else:
    st.error("⚠ Could not fetch live crypto data. Check Alpha Vantage API.")

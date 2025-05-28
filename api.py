import pickle
import pandas as pd
import numpy as np
from fastapi import FastAPI
from pydantic import BaseModel
from config import DATA_FOLDER

# Load the trained model
model_path = f"{DATA_FOLDER}model.pkl"
with open(model_path, "rb") as file:
    model = pickle.load(file)

# Initialize FastAPI app
app = FastAPI()

# Define request format
class PriceData(BaseModel):
    open: float
    high: float
    low: float
    close: float
    volume: float
    MA_10: float
    MA_50: float
    RSI: float

# API Route: Predict Price Movement
@app.post("/predict/")
def predict_price(data: PriceData):
    try:
        # Convert input data to a DataFrame
        input_data = pd.DataFrame([data.dict()])
        
        # Make prediction
        prediction = model.predict(input_data)[0]
        prediction_label = "Up" if prediction == 1 else "Down"

        return {"prediction": prediction_label}

    except Exception as e:
        return {"error": str(e)}

# Root route
@app.get("/")
def home():
    return {"message": "Crypto Price Prediction API is Running!"}

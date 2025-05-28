import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score
from config import DATA_FOLDER

# Load the preprocessed data
df = pd.read_csv(f"{DATA_FOLDER}BTCUSDT_preprocessed.csv")

# Define the target variable (1 = price up, 0 = price down)
df["Price_Change"] = df["close"].diff()
df["Target"] = (df["Price_Change"] > 0).astype(int)

# Select features and target variable
features = ["open", "high", "low", "close", "volume", "MA_10", "MA_50", "RSI"]

# Shift the feature dataset so we predict the next day's movement
X = df[features].shift(1)

# Define the target variable (1 = price up, 0 = price down)
df["Price_Change"] = df["close"].diff()
df["Target"] = (df["Price_Change"] > 0).astype(int)

# Drop NaN values from both `X` and `df` to ensure they are aligned
df.dropna(inplace=True)
X = X.loc[df.index]  # Align X with the remaining valid rows in df
y = df["Target"]

# Ensure X and y are the same length
print(f"✅ X shape: {X.shape}, y shape: {y.shape}")

# Split data into training and testing sets (80% train, 20% test)
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)


# Train a Random Forest Classifier
model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

# Evaluate model accuracy
y_pred = model.predict(X_test)
accuracy = accuracy_score(y_test, y_pred)
print(f"✅ Model Accuracy: {accuracy:.2f}")

# Save the trained model
import pickle
with open(f"{DATA_FOLDER}model.pkl", "wb") as f:
    pickle.dump(model, f)

print("✅ Model saved as 'model.pkl'!")

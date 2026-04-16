"""
Single‑file fraud detection system.
No MCP, no separate module imports needed.
"""

import random
import pandas as pd
import logging
import numpy as np
from sklearn.ensemble import IsolationForest
import joblib
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Rules Tools (inline from rules_tools.py)
# -------------------------------------------------------------------
def check_amount(amount: float, avg_amount: float) -> int:
    """Compare transaction amount to user's normal behavior. Returns 0-3."""
    if avg_amount <= 0:
        avg_amount = 1
    ratio = amount / avg_amount
    if ratio >= 5:
        return 3
    elif ratio >= 3:
        return 2
    elif ratio >= 2:
        return 1
    else:
        return 0

def check_country(user_country: str, transaction_country: str, usually_international: bool) -> int:
    """Check country mismatch. Returns 0-3."""
    is_international = user_country != transaction_country
    if is_international and not usually_international:
        return 3
    elif is_international and usually_international:
        return 1
    else:
        return 0

# -------------------------------------------------------------------
# Anomaly Detection (inline from anomaly.py)
# -------------------------------------------------------------------
MODEL_PATH = "isolation_forest_model.pkl"

def train_and_save_model():
    """Train Isolation Forest on synthetic normal amounts."""
    X_train = np.array([
        [100], [200], [150], [300], [250],
        [400], [500], [350], [450], [600]
    ])
    model = IsolationForest(contamination=0.01, random_state=42)
    model.fit(X_train)
    joblib.dump(model, MODEL_PATH)
    logger.info("Model trained and saved to %s", MODEL_PATH)
    return model

def load_model():
    """Load model from disk or train new one."""
    if os.path.exists(MODEL_PATH):
        logger.info("Loading existing model from %s", MODEL_PATH)
        return joblib.load(MODEL_PATH)
    else:
        logger.warning("Model file not found. Training new model.")
        return train_and_save_model()

# Global model loaded once at import
detector = load_model()

def check_anomaly(amount: float) -> int:
    """Detect amount anomalies. Returns 3 if anomalous, else 0."""
    prediction = detector.predict([[amount]])
    return 3 if prediction[0] == -1 else 0

def check_velocity(transactions_last_hour: int) -> int:
    """Detect high‑frequency spikes. Returns 0-3."""
    if transactions_last_hour > 10:
        return 3
    if transactions_last_hour > 5:
        return 2
    return 0

# -------------------------------------------------------------------
# Simulated user context (stubs – replace with real DB later)
# -------------------------------------------------------------------
def get_user_profile(user_id: str):
    """Return avg_amount and international flag for a user."""
    profiles = {
        "user_1": {"avg_amount": 5000.0, "usually_international": False},
        "user_2": {"avg_amount": 12000.0, "usually_international": True},
    }
    return profiles.get(user_id, {"avg_amount": 5000.0, "usually_international": False})

def get_velocity(user_id: str) -> int:
    """Return number of transactions in the last hour."""
    return random.randint(0, 12)

# -------------------------------------------------------------------
# Main Orchestration
# -------------------------------------------------------------------
def main():
    # 1. Load data
    try:
        df = pd.read_excel("fraud_simulation.xlsx")
        df = df.rename(columns={
            "Amount": "amount",
            "User Country": "user_country",
            "Transaction Country": "transaction_country",
            "Failed Attempts": "failed_attempts"
        })
    except Exception as e:
        logger.error("Error loading data: %s", e)
        return

    logger.info("--- FRAUD DETECTION RUNNER STARTED ---")

    # 2. Process each transaction (first 10 for demonstration)
    for i, row in df.head(10).iterrows():
        tx = row.to_dict()
        user_id = f"user_{i % 2 + 1}"   # alternate between user_1 and user_2
        logger.info("Processing transaction ID %s (user: %s)", i+1, user_id)

        profile = get_user_profile(user_id)
        velocity_count = get_velocity(user_id)

        amount_score = check_amount(tx['amount'], profile['avg_amount'])
        country_score = check_country(
            tx['user_country'],
            tx['transaction_country'],
            profile['usually_international']
        )
        anomaly_score = check_anomaly(tx['amount'])
        velocity_score = check_velocity(velocity_count)

        total = amount_score + country_score + anomaly_score + velocity_score

        if total <= 2:
            decision = "SAFE"
        elif total <= 5:
            decision = "SUSPICIOUS"
        else:
            decision = "FRAUD"

        logger.info(
            "Scores → Amount: %d, Country: %d, Anomaly: %d, Velocity: %d",
            amount_score, country_score, anomaly_score, velocity_score
        )
        logger.info("Total: %d → Decision: %s\n", total, decision)

if __name__ == "__main__":
    main()
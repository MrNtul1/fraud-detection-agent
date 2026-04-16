"""
Single‑process fraud detection runner.
Uses rules_tools and anomaly modules directly.
No MCP or network required.
"""

import random
import pandas as pd
import logging
from rules_tools import check_amount, check_country
from anomaly import check_anomaly

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


# -------------------------------------------------------------------
# Simulated user profile & velocity lookups
# -------------------------------------------------------------------
def get_user_profile(user_id: str):
    """Stub – replace with database lookup."""
    profiles = {
        "user_1": {"avg_amount": 5000.0, "usually_international": False},
        "user_2": {"avg_amount": 12000.0, "usually_international": True},
    }
    return profiles.get(user_id, {"avg_amount": 5000.0, "usually_international": False})


def get_velocity(user_id: str) -> int:
    """Stub – query time‑series store for count in last hour."""
    return random.randint(0, 12)


def check_velocity(transactions_last_hour: int) -> int:
    """Detect high‑frequency transaction spikes. Returns 0-3."""
    if transactions_last_hour > 10:
        return 3
    if transactions_last_hour > 5:
        return 2
    return 0


# -------------------------------------------------------------------
# Main processing
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
        # Simulate user ID (in real data you'd have a user_id column)
        user_id = f"user_{i % 2 + 1}"
        logger.info("Processing transaction ID %s (user: %s)", i+1, user_id)

        # Fetch user context
        profile = get_user_profile(user_id)
        velocity_count = get_velocity(user_id)

        # Calculate risk scores using the original functions
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
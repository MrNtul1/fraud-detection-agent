"""
Self‑contained LLM fraud detection orchestrator.
No imports from tools/ – all deterministic functions are embedded.
Uses OpenRouter function calling.
"""
import asyncio
import json
import logging
import random
import os
import numpy as np
import joblib
import pandas as pd
from sklearn.ensemble import IsolationForest
from openai import AsyncOpenAI

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# -------------------------------------------------------------------
# Deterministic Tools (inline from rules_tools and anomaly_tools)
# -------------------------------------------------------------------
def check_amount(amount: float, avg_amount: float) -> int:
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
    is_international = user_country != transaction_country
    if is_international and not usually_international:
        return 3
    elif is_international and usually_international:
        return 1
    else:
        return 0

def check_velocity(transactions_last_hour: int) -> int:
    if transactions_last_hour > 10:
        return 3
    if transactions_last_hour > 5:
        return 2
    return 0

# -------------------------------------------------------------------
# Anomaly Detection (inline with model persistence)
# -------------------------------------------------------------------
MODEL_PATH = "isolation_forest_model.pkl"

def train_and_save_model():
    X_train = np.array([[100], [200], [150], [300], [250],
                        [400], [500], [350], [450], [600]])
    model = IsolationForest(contamination=0.01, random_state=42)
    model.fit(X_train)
    joblib.dump(model, MODEL_PATH)
    logger.info("Model trained and saved to %s", MODEL_PATH)
    return model

def load_model():
    if os.path.exists(MODEL_PATH):
        logger.info("Loading existing model from %s", MODEL_PATH)
        return joblib.load(MODEL_PATH)
    else:
        logger.warning("Model file not found. Training new model.")
        return train_and_save_model()

detector = load_model()

def check_anomaly(amount: float) -> int:
    prediction = detector.predict([[amount]])
    return 3 if prediction[0] == -1 else 0

# -------------------------------------------------------------------
# OpenRouter LLM Client (inline)
# -------------------------------------------------------------------
class OpenRouterLLM:
    def __init__(self):
        self.client = AsyncOpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=os.getenv("OPENROUTER_API_KEY")
        )
        self.model = "meta-llama/llama-3.1-70b-instruct"

# -------------------------------------------------------------------
# Simulated user context
# -------------------------------------------------------------------
def get_user_profile(user_id: str):
    profiles = {
        "user_1": {"avg_amount": 5000.0, "usually_international": False},
        "user_2": {"avg_amount": 12000.0, "usually_international": True},
    }
    return profiles.get(user_id, {"avg_amount": 5000.0, "usually_international": False})

def get_velocity_count(user_id: str) -> int:
    return random.randint(0, 12)

# -------------------------------------------------------------------
# Tool definitions for LLM function calling
# -------------------------------------------------------------------
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "check_amount_tool",
            "description": "Compare transaction amount to user's average. Returns risk score 0-3.",
            "parameters": {
                "type": "object",
                "properties": {
                    "amount": {"type": "number"},
                    "avg_amount": {"type": "number"}
                },
                "required": ["amount", "avg_amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_country_tool",
            "description": "Check country mismatch. Returns 0-3.",
            "parameters": {
                "type": "object",
                "properties": {
                    "user_country": {"type": "string"},
                    "transaction_country": {"type": "string"},
                    "usually_international": {"type": "boolean"}
                },
                "required": ["user_country", "transaction_country", "usually_international"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_anomaly_tool",
            "description": "ML anomaly detection on amount. Returns 3 if anomalous, else 0.",
            "parameters": {
                "type": "object",
                "properties": {"amount": {"type": "number"}},
                "required": ["amount"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "check_velocity_tool",
            "description": "Check transaction frequency last hour. Returns 0-3.",
            "parameters": {
                "type": "object",
                "properties": {"transactions_last_hour": {"type": "integer"}},
                "required": ["transactions_last_hour"]
            }
        }
    }
]

TOOL_MAP = {
    "check_amount_tool": check_amount,
    "check_country_tool": check_country,
    "check_anomaly_tool": check_anomaly,
    "check_velocity_tool": check_velocity
}

# -------------------------------------------------------------------
# LLM Orchestration Logic
# -------------------------------------------------------------------
async def process_transaction(llm: OpenRouterLLM, tx: dict, user_id: str):
    profile = get_user_profile(user_id)
    velocity = get_velocity_count(user_id)

    user_message = f"""
Transaction details:
- Amount: ${tx['amount']}
- User country: {tx['user_country']}
- Transaction country: {tx['transaction_country']}
- Failed attempts: {tx.get('failed_attempts', 0)}

User context:
- Average transaction amount: ${profile['avg_amount']}
- Usually international: {profile['usually_international']}
- Transactions last hour: {velocity}

Use the available fraud detection tools as needed, then output EXACTLY one word: SAFE, SUSPICIOUS, or FRAUD.
"""

    messages = [{"role": "user", "content": user_message}]

    while True:
        response = await llm.client.chat.completions.create(
            model=llm.model,
            messages=messages,
            tools=TOOLS,
            tool_choice="auto"
        )
        message = response.choices[0].message

        if message.tool_calls:
            messages.append(message)
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)
                result = TOOL_MAP[tool_name](**args)
                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": str(result)
                })
        else:
            return message.content.strip()

# -------------------------------------------------------------------
# Main
# -------------------------------------------------------------------
async def main():
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

    llm = OpenRouterLLM()
    logger.info("--- LLM FRAUD DETECTION RUNNER STARTED ---")

    for i, row in df.head(5).iterrows():
        tx = row.to_dict()
        user_id = f"user_{i % 2 + 1}"
        logger.info("Processing transaction ID %s (user: %s)", i+1, user_id)
        decision = await process_transaction(llm, tx, user_id)
        logger.info("LLM Decision: %s\n", decision)

if __name__ == "__main__":
    asyncio.run(main())
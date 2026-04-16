import asyncio
import pandas as pd
from mcp_agent.app import MCPApp
from gemini_llm import GeminiLLM

from agents import (
    orchestrator_agent,
    amount_agent,
    country_agent,
    anomaly_agent
)

app = MCPApp(name="fraud_hierarchical_app")


def load_transactions():
    df = pd.read_csv("transactions.csv")
    return df

async def process_transaction(llm, transaction: dict):

    # Format transaction for LLM
    message = f"""
Analyze this transaction using available tools:

Amount: {transaction['amount']}
Average Amount: {transaction['avg_amount']}
User Country: {transaction['user_country']}
Transaction Country: {transaction['transaction_country']}
Usually International: {transaction['usually_international']}
Transactions Last Hour: {transaction['transactions_last_hour']}

Decide fraud risk using tools only.
Return final decision.
"""
    
     # Ask LLM to orchestrate tools + decide
    result = await llm.generate_str(message=message)

    return result   

async def main():

    async with app.run():

        async with orchestrator_agent:

            # Attach LLM (the brain)
           llm = GeminiLLM()
           
           df = load_transactions()
           print("\n FRAUD RUNNER STARTED\n")
           results = []
           # Loop through all transactions
           for i, row in df.iterrows():

                transaction = row.to_dict()

                print(f"\n🔍 Processing transaction {i+1}")

                result = await process_transaction(llm, transaction)

                print("Decision:", result)

                results.append({
                    "transaction_id": i,
                    "decision": result
                })

        print("\n FINAL RESULTS:")
        for r in results:
            print(r)


if __name__ == "__main__":
    asyncio.run(main())
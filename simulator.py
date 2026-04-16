import random
import pandas as pd

# Load your file
df = pd.read_excel("fraud_simulation_updated.xlsx")

# Show first rows
print(df.head())

def check_amount(amount):
    return "High_Risk" if amount > 10000 else "LOW_RISK"

def check_country(user_country, transaction_country):
    return "High_risk"if user_country != transaction_country else "Low_risk"
def check_anomaly(amount):
    return "ANOMALY" if amount > 7000 else "NORMAL"

def orchestrator(transaction):
    amount = transaction["amount"]
    user_country = transaction["user_country"]
    transaction_country = transaction["transaction_country"]
    
    print("\n New TRANSACTION: \n")
    print(transaction)
    
    results = {}
    
    if amount > 10000:
        print("Decision: High amount → skip other checks")
        return "FRAUD", amount
    results["amount"] = check_amount(amount)
    
    if user_country != transaction_country:
        results["country"] = check_country(user_country, transaction_country)
    if results["amount"] == "LOW_RISK" and "country" not in results:
        results["anomaly"] = check_anomaly(amount)   
    print("Tool results", results)       
        
    if results.get("amount") == "HIGH_RISK":
       return "FRAUD", amount

    if results.get("country") == "HIGH_RISK":
       return "FRAUD", amount

    if results.get("anomaly") == "ANOMALY":
       return "SUSPICIOUS", amount

    return "SAFE", amount

def generate_transaction():
    countries = ["South Africa", "Nigeria", "Kenya", "USA"]

    return {
        "amount": random.randint(100, 20000),
        "user_country": random.choice(countries),
        "transaction_country": random.choice(countries),
    }

def run_simulation(n=50):
    fraud_count = 0
    suspicious_count = 0
    safe_count = 0
    fraud_value = 0
    
    for _ in range(n):
        transaction = generate_transaction()
        
        result, amount = orchestrator(transaction)
        
        print("Final decision", result)
        
        if result == "FRAUD":
            fraud_count +=1
            fraud_value += amount
        elif result == "SUSPICIOUS":
            suspicious_count += 1
        else:
            safe_count += 1
    print("\n===== SIMULATION RESULTS =====")
    print(f"Total Transactions: {n}")
    print(f"Fraud Detected: {fraud_count}")
    print(f"Suspicious: {suspicious_count}")
    print(f"Safe: {safe_count}")
    print(f"Total Fraud Value Detected: {fraud_value}")
            
if __name__ == "__main__":
    run_simulation(20)       
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
      
        
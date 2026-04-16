import random
def generate_normal_tranaction():
    return{
        "amount": random.randint(100, 1000),
        "country": "South Africa"
    }
def generate_fraud_transaction():
    return {
        "amount": random.randint(10000, 20000),
        "country": random.choice(["Nigeria", "Brazil", "Russia"])
    }
def generate_dataset(n_normal=50, n_fraud=20):
    data= []
    for _ in range(n_normal):
        data.append(generate_normal_tranaction())
    for _ in range(n_fraud):
        data.append(generate_fraud_transaction())
    random.shuffle(data)
    return data

if __name__ == "__main__":
    dataset = generate_dataset()
    for d in dataset[:5]:
        print(d)
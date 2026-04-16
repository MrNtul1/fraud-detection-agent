#here i am creating 3 tools that my AI will use(check amount, check country, final decision)

from fastmcp import FastMCP
from anomaly_model import check_anomaly

mcp = FastMCP("Fraud Detection Server")

#rule 1 check amount  this is just to test  basically using a threshold
@mcp.tool
def amount_risk(amount, avg_amount):
    ratio = amount / avg_amount

    if ratio > 5:
        return 3
    elif ratio > 2:
        return 2
    return 0

@mcp.tool
def location_risk(
    user_country: str,
    transaction_country: str,
    usually_international: bool
) -> int:
    """
    Risk based on whether international transactions are normal for this user
    """

    is_international = user_country != transaction_country

    # If it's local → always safe
    if not is_international:
        return 0

    # If user normally does international → low risk
    if usually_international:
        return 0

    # If user NEVER does international → suspicious
    return 2

#  Velocity Analyst (FAILED ATTEMPTS)
@mcp.tool
def velocity_risk(failed_attempts: int) -> int:
    """Returns risk score based on failed attempts"""
    if failed_attempts > 3:
        return 3
    elif failed_attempts > 1:
        return 2
    return 0

@mcp.tool
def anomaly_risk(
    amount: int,
    avg_amount: int,
    transaction_count_last_hour: int
) -> int:
    """
    Detects unusual behavior based on deviation from normal patterns
    """

    score = 0

    # Amount deviation
    if avg_amount > 0:
        ratio = amount / avg_amount

        if ratio > 5:
            score += 2
        elif ratio > 2:
            score += 1

    # Activity spike
    if transaction_count_last_hour > 5:
        score += 2
    elif transaction_count_last_hour > 3:
        score += 1

    return min(score, 3)

@mcp.tool 
def final_decision(amount_risk: str, country_risk: str)->str:
    """Combine risk signals and return final fraud detection"""
    if amount_risk == "High_risk" or country_risk =="High_risk":
        return "FRAUD"
    return "SAFE"

if __name__=="__main__":
    mcp.run()
    
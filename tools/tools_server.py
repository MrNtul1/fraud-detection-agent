from fastmcp import FastMCP
from anomaly_tools import check_anomaly
from rules_tools import check_amount, check_country

mcp = FastMCP("Fraud Tools Server")


@mcp.tool
def check_amount_tool(amount: float, avg_amount: float) -> int:
    return check_amount(amount, avg_amount)


@mcp.tool
def check_country_tool(user_country: str, transaction_country: str, usually_international: bool) -> int:
    return check_country(user_country, transaction_country, usually_international)


@mcp.tool
def check_anomaly_tool(amount: float) -> int:
    return check_anomaly(amount)


if __name__ == "__main__":
    mcp.run()
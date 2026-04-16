from mcp_agent.agents.agent import Agent

anomaly_agent = Agent(
    name="anomaly_checker",
    instruction="""
Detect anomalies using behavior patterns.

Use check_anomaly_tool.

Return ONLY a number (0–3)
""",
    server_names=["fastmcp"]
)
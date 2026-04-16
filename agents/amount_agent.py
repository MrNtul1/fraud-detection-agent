from mcp_agent.agents.agent import Agent

amount_agent = Agent(
    name="amount_checker",
    instruction="""
Check amount risk relative to user behavior.

Use check_amount_tool.

Return ONLY a number (0–3)
""",
    server_names=["fastmcp"]
)
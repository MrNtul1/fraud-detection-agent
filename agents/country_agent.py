from mcp_agent.agents.agent import Agent

# Sub-agent: Country
country_agent = Agent(
    name="country_checker",
    instruction="""
    You ONLY check if countries mismatch.

    Use check_country tool.

    Return ONLY:
    HIGH_RISK or LOW_RISK
    """,
    server_names=["fastmcp"]
)
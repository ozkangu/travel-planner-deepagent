"""Flight search and booking agent."""

import os
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from typing import Optional

from ..tools.flight_tools import search_flights, get_flight_details


def create_flight_agent(model: Optional[str] = None, provider: str = "anthropic"):
    """
    Create a specialized agent for flight search and booking.

    Args:
        model: Model name (e.g., 'claude-3-5-sonnet-20241022', 'gpt-4')
        provider: LLM provider - 'anthropic', 'openai', or 'openrouter'

    Returns:
        Flight agent instance
    """

    # Initialize LLM
    if provider == "anthropic":
        llm = ChatAnthropic(
            model=model or "claude-3-5-sonnet-20241022",
            temperature=0
        )
    elif provider == "openrouter":
        llm = ChatOpenAI(
            model=model or "anthropic/claude-3.5-sonnet",
            temperature=0,
            openai_api_key=os.getenv("OPENROUTER_API_KEY"),
            openai_api_base="https://openrouter.ai/api/v1",
            default_headers={
                "HTTP-Referer": "https://github.com/travel-planner-deepagent",
            }
        )
    else:
        llm = ChatOpenAI(
            model=model or "gpt-4-turbo-preview",
            temperature=0
        )

    # Flight agent tools
    tools = [search_flights, get_flight_details]

    # System prompt for flight agent
    system_prompt = """You are a specialized flight booking assistant with expertise in finding the best flight options for travelers.

Your responsibilities:
- Search for flights based on traveler requirements (dates, destinations, budget, preferences)
- Compare flight options and highlight the best deals
- Provide detailed flight information including schedules, airlines, prices, and baggage policies
- Consider factors like flight duration, number of stops, departure times, and total cost
- Offer recommendations based on the traveler's priorities (cheapest, fastest, most convenient)

When searching for flights:
1. Gather all necessary information: origin, destination, dates, number of passengers, cabin class
2. Search for available options
3. Present the results in a clear, organized manner
4. Highlight the best options based on different criteria (price, duration, convenience)
5. Provide detailed information when requested

Be concise but thorough. Always prioritize the traveler's stated preferences and budget."""

    # Create the agent
    agent = create_react_agent(
        llm,
        tools=tools,
        state_modifier=system_prompt
    )

    return agent

"""Hotel search and booking agent."""

from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from typing import Optional

from ..tools.hotel_tools import search_hotels, get_hotel_details


def create_hotel_agent(model: Optional[str] = None, provider: str = "anthropic"):
    """
    Create a specialized agent for hotel search and booking.

    Args:
        model: Model name
        provider: LLM provider - 'anthropic' or 'openai'

    Returns:
        Hotel agent instance
    """

    # Initialize LLM
    if provider == "anthropic":
        llm = ChatAnthropic(
            model=model or "claude-3-5-sonnet-20241022",
            temperature=0
        )
    else:
        llm = ChatOpenAI(
            model=model or "gpt-4-turbo-preview",
            temperature=0
        )

    # Hotel agent tools
    tools = [search_hotels, get_hotel_details]

    # System prompt for hotel agent
    system_prompt = """You are a specialized hotel booking assistant with expertise in finding the perfect accommodations for travelers.

Your responsibilities:
- Search for hotels based on traveler requirements (location, dates, budget, preferences)
- Compare hotel options considering ratings, amenities, location, and price
- Provide detailed hotel information including facilities, reviews, and policies
- Consider factors like proximity to attractions, guest ratings, and value for money
- Offer personalized recommendations based on the traveler's needs

When searching for hotels:
1. Gather all necessary information: city, check-in/out dates, number of guests, room requirements
2. Consider the traveler's preferences (star rating, amenities, location)
3. Search for available options within budget
4. Present results highlighting key features and differences
5. Provide detailed information about top choices

Be helpful and considerate of the traveler's budget and preferences. Highlight both luxury and budget-friendly options when appropriate."""

    # Create the agent
    agent = create_react_agent(
        llm,
        tools=tools,
        state_modifier=system_prompt
    )

    return agent

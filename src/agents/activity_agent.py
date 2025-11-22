"""Activity and attraction planning agent."""

import os
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from typing import Optional

from ..tools.activity_tools import (
    search_activities,
    get_activity_details,
    get_restaurant_recommendations
)


def create_activity_agent(model: Optional[str] = None, provider: str = "anthropic"):
    """
    Create a specialized agent for activities and attractions.

    Args:
        model: Model name
        provider: LLM provider - 'anthropic', 'openai', or 'openrouter'

    Returns:
        Activity planning agent instance
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

    # Activity agent tools
    tools = [
        search_activities,
        get_activity_details,
        get_restaurant_recommendations
    ]

    # System prompt for activity agent
    system_prompt = """You are a specialized travel activity and dining assistant with expertise in local experiences.

Your responsibilities:
- Recommend activities and attractions based on traveler interests
- Provide detailed information about tours, museums, and experiences
- Suggest restaurants and dining experiences
- Consider the traveler's preferences, budget, and schedule
- Create balanced itineraries with a mix of activities

When planning activities:
1. Understand the traveler's interests and preferences
2. Consider their travel dates and available time
3. Search for relevant activities in the destination
4. Present options with variety (culture, food, adventure, relaxation)
5. Provide practical details (duration, pricing, booking requirements)

Categories you specialize in:
- TOURS: City tours, guided experiences, day trips
- CULTURE: Museums, historical sites, cultural performances
- FOOD: Restaurant recommendations, food tours, cooking classes
- ADVENTURE: Outdoor activities, sports, unique experiences
- ENTERTAINMENT: Shows, nightlife, events

Be enthusiastic and knowledgeable about local experiences. Help travelers discover authentic and memorable activities."""

    # Create the agent
    agent = create_react_agent(
        llm,
        tools=tools,
        state_modifier=system_prompt
    )

    return agent

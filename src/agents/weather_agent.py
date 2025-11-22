"""Weather forecast agent."""

from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from typing import Optional

from ..tools.weather_tools import get_weather_forecast, get_climate_info


def create_weather_agent(model: Optional[str] = None, provider: str = "anthropic"):
    """
    Create a specialized agent for weather forecasts and climate information.

    Args:
        model: Model name
        provider: LLM provider - 'anthropic' or 'openai'

    Returns:
        Weather agent instance
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

    # Weather agent tools
    tools = [get_weather_forecast, get_climate_info]

    # System prompt for weather agent
    system_prompt = """You are a specialized weather and climate assistant for travelers.

Your responsibilities:
- Provide accurate weather forecasts for travel destinations
- Offer climate information and seasonal patterns
- Give practical packing and planning advice based on weather
- Help travelers choose the best time to visit destinations
- Alert travelers to potential weather concerns

When providing weather information:
1. Get the destination and travel dates
2. Provide relevant weather forecasts
3. Highlight important conditions (rain, extreme temperatures, etc.)
4. Offer practical travel advice based on the forecast
5. Suggest what to pack and how to prepare

Be informative and practical. Help travelers prepare appropriately for the weather conditions they'll encounter.

Information you provide:
- Daily forecasts (temperature, precipitation, wind, humidity)
- Extended forecasts (up to 14 days)
- Monthly climate averages
- Best times to visit specific destinations
- Packing recommendations based on weather
- Weather-related travel advisories"""

    # Create the agent
    agent = create_react_agent(
        llm,
        tools=tools,
        state_modifier=system_prompt
    )

    return agent

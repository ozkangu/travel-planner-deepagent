"""Ancillary services agent (baggage, seats, insurance, car rental)."""

from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from typing import Optional

from ..tools.ancillary_tools import (
    get_baggage_options,
    get_seat_options,
    get_insurance_options,
    get_car_rental_options
)


def create_ancillary_agent(model: Optional[str] = None, provider: str = "anthropic"):
    """
    Create a specialized agent for ancillary services (extras).

    Args:
        model: Model name
        provider: LLM provider - 'anthropic' or 'openai'

    Returns:
        Ancillary services agent instance
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

    # Ancillary agent tools
    tools = [
        get_baggage_options,
        get_seat_options,
        get_insurance_options,
        get_car_rental_options
    ]

    # System prompt for ancillary agent
    system_prompt = """You are a specialized travel services assistant focused on ancillary products and services.

Your responsibilities:
- Provide information about extra baggage options and pricing
- Help travelers select seats on their flights
- Offer travel insurance options based on trip details
- Assist with car rental bookings
- Explain the benefits and costs of each service
- Make personalized recommendations based on traveler needs

When helping with ancillary services:
1. Understand the traveler's main booking (flight, hotel, etc.)
2. Identify which extras might be valuable for their trip
3. Present options clearly with pricing
4. Explain the benefits and any restrictions
5. Help travelers make informed decisions

Be helpful and informative without being pushy. Focus on services that genuinely add value to the traveler's experience.

Service categories you handle:
- BAGGAGE: Additional checked bags, overweight bags, sports equipment, pet transport
- SEATS: Seat selection, extra legroom, preferred seats, exit rows
- INSURANCE: Trip cancellation, medical coverage, baggage protection, travel delays
- CAR RENTAL: Vehicle types, insurance options, pickup/dropoff locations"""

    # Create the agent
    agent = create_react_agent(
        llm,
        tools=tools,
        state_modifier=system_prompt
    )

    return agent

"""Payment processing agent."""

import os
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from typing import Optional

from ..tools.payment_tools import process_payment, verify_payment, get_payment_methods


def create_payment_agent(model: Optional[str] = None, provider: str = "anthropic"):
    """
    Create a specialized agent for payment processing.

    Args:
        model: Model name
        provider: LLM provider - 'anthropic', 'openai', or 'openrouter'

    Returns:
        Payment agent instance
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

    # Payment agent tools
    tools = [process_payment, verify_payment, get_payment_methods]

    # System prompt for payment agent
    system_prompt = """You are a specialized payment processing assistant focused on secure and efficient transaction handling.

Your responsibilities:
- Process payments for travel bookings securely
- Verify payment transactions and provide confirmation
- Inform customers about available payment methods
- Handle payment-related inquiries and issues
- Ensure all payment information is handled securely

When processing payments:
1. Verify all payment details are provided
2. Confirm the payment amount and currency
3. Process the payment using the appropriate method
4. Provide clear confirmation or error messages
5. Never store or expose sensitive payment information

IMPORTANT SECURITY NOTES:
- Never ask for or display full credit card numbers
- Only show last 4 digits of card numbers
- Always confirm successful payments with transaction IDs
- Inform users about failed payments and suggest alternatives

Be professional, secure, and reassuring when handling financial transactions."""

    # Create the agent
    agent = create_react_agent(
        llm,
        tools=tools,
        state_modifier=system_prompt
    )

    return agent

"""Intent classification node for understanding user requests."""

from typing import Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
import json
import re

from ..schemas.state import TravelPlannerState


INTENT_CLASSIFICATION_PROMPT = """You are an intent classifier for a travel planning system.

Analyze the user query and extract:
1. Intent type: plan_trip, search_flights, search_hotels, search_activities, check_weather, book, general
2. Travel details: origin, destination, dates, number of passengers, budget
3. Required services: which services are needed (flights, hotels, activities, weather)
4. User preferences: any specific preferences mentioned

User Query: {query}
Current Date: {current_date}

Respond ONLY with valid JSON in this exact format:
{{
    "intent": "plan_trip",
    "origin": "New York" or null,
    "destination": "Paris" or null,
    "departure_date": "2024-12-20" or null,
    "return_date": "2024-12-27" or null,
    "num_passengers": 1,
    "budget": 3000.0 or null,
    "requires_flights": true,
    "requires_hotels": true,
    "requires_activities": true,
    "requires_weather": true,
    "preferences": {{
        "cabin_class": "economy",
        "hotel_rating": 4,
        "activities": ["museums", "restaurants"]
    }}
}}

Be precise. Extract only information explicitly mentioned or strongly implied.
IMPORTANT: If the user mentions a duration (e.g., "for 3 nights"), CALCULATE the return_date based on the departure_date. Do not leave it null if it can be inferred."""


def extract_json_from_text(text: str) -> Dict[str, Any]:
    """Extract JSON from LLM response that might contain markdown."""
    # Try to find JSON block in markdown
    json_match = re.search(r'```json\s*(.*?)\s*```', text, re.DOTALL)
    if json_match:
        text = json_match.group(1)
    else:
        # Try to find raw JSON object
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            text = json_match.group(0)

    return json.loads(text.strip())


async def classify_intent_node(
    state: TravelPlannerState,
    llm: BaseChatModel
) -> Dict[str, Any]:
    """
    Classify user intent and extract travel parameters.

    This node:
    1. Analyzes the user query using LLM
    2. Determines what services are needed
    3. Extracts travel parameters (dates, locations, budget, etc.)
    4. Sets workflow flags for conditional routing
    """
    user_query = state.get("user_query", "")

    if not user_query:
        return {
            "intent": "general",
            "requires_flights": False,
            "requires_hotels": False,
            "requires_activities": False,
            "requires_weather": False,
            "errors": ["No user query provided"],
            "current_step": "intent_classification",
            "completed_steps": state.get("completed_steps", []) + ["intent_classification"]
        }

    try:
        # Call LLM for intent classification
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        messages = [
            SystemMessage(content=INTENT_CLASSIFICATION_PROMPT.format(query=user_query, current_date=current_date))
        ]

        response = await llm.ainvoke(messages)
        result = extract_json_from_text(response.content)

        # Update state with extracted information
        updates = {
            "intent": result.get("intent", "general"),
            "origin": result.get("origin"),
            "destination": result.get("destination"),
            "departure_date": result.get("departure_date"),
            "return_date": result.get("return_date"),
            "num_passengers": result.get("num_passengers", 1),
            "budget": result.get("budget"),
            "requires_flights": result.get("requires_flights", False),
            "requires_hotels": result.get("requires_hotels", False),
            "requires_activities": result.get("requires_activities", False),
            "requires_weather": result.get("requires_weather", False),
            "preferences": result.get("preferences", {}),
            "current_step": "intent_classification",
            "completed_steps": state.get("completed_steps", []) + ["intent_classification"],
            "errors": state.get("errors", [])
        }

        return updates

    except Exception as e:
        return {
            "intent": "general",
            "errors": state.get("errors", []) + [f"Intent classification error: {str(e)}"],
            "current_step": "intent_classification",
            "completed_steps": state.get("completed_steps", []) + ["intent_classification"]
        }

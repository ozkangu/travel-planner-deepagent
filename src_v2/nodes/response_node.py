"""Response generation node for the travel planner."""

from typing import Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage

from ..schemas.state import TravelPlannerState


RESPONSE_PROMPT = """You are a helpful and enthusiastic travel assistant.

Your goal is to provide a natural, conversational response to the user based on their query and the results of any actions taken.

**User Query:** {query}

**Intent:** {intent}

**Search Results:**
{search_summary}

**Itinerary:**
{itinerary}

**Errors:**
{errors}

**Instructions:**
1. Answer the user's query directly.
2. If search results are available, summarize them clearly (e.g., "I found 3 flight options starting at $200..."). Do NOT list every single detail unless asked, but give enough info to be useful.
3. If an itinerary was generated, present it or refer to it enthusiastically.
4. If there were errors (e.g., missing parameters), explain what is needed to proceed (e.g., "I need to know your destination to find hotels").
5. If the intent was just "general" (e.g., "Hello"), respond politely and offer help with travel planning.
6. Be concise but warm.

**Response:**"""


async def generate_response_node(
    state: TravelPlannerState,
    llm: BaseChatModel
) -> Dict[str, Any]:
    """
    Generate a natural language response based on the current state.
    """
    try:
        user_query = state.get("user_query", "")
        intent = state.get("intent", "general")
        errors = state.get("errors", [])
        itinerary = state.get("itinerary")

        # Summarize search results
        search_summary_parts = []
        
        # Flights
        flight_options = state.get("flight_options", [])
        if flight_options:
            search_summary_parts.append(f"Found {len(flight_options)} flight options.")
            for i, f in enumerate(flight_options[:3]):
                search_summary_parts.append(f"- Flight {i+1}: {f.get('airline')} to {f.get('destination')}, ${f.get('price')}, {f.get('departure_time')}")
        
        # Hotels
        hotel_options = state.get("hotel_options", [])
        if hotel_options:
            search_summary_parts.append(f"\nFound {len(hotel_options)} hotel options.")
            for i, h in enumerate(hotel_options[:3]):
                search_summary_parts.append(f"- Hotel {i+1}: {h.get('name')}, {h.get('rating')} stars, ${h.get('price_per_night')}/night")

        # Activities
        activity_options = state.get("activity_options", [])
        if activity_options:
            search_summary_parts.append(f"\nFound {len(activity_options)} activity options.")
            for i, a in enumerate(activity_options[:3]):
                search_summary_parts.append(f"- Activity {i+1}: {a.get('name')}, ${a.get('price')}")

        # Weather
        weather_forecast = state.get("weather_forecast", [])
        if weather_forecast:
            search_summary_parts.append(f"\nWeather forecast available for {len(weather_forecast)} days.")
            if len(weather_forecast) > 0:
                w = weather_forecast[0]
                search_summary_parts.append(f"- {w.get('date')}: {w.get('condition')}, {w.get('temperature')}°C")

        search_summary = "\n".join(search_summary_parts) if search_summary_parts else "No specific search results."

        # Format prompt
        prompt = RESPONSE_PROMPT.format(
            query=user_query,
            intent=intent,
            search_summary=search_summary,
            itinerary=itinerary if itinerary else "No itinerary generated yet.",
            errors="\n".join(errors) if errors else "No errors."
        )

        # Generate response
        response = await llm.ainvoke([SystemMessage(content=prompt)])
        
        return {
            "response": response.content,
            "current_step": "response_generation",
            "completed_steps": state.get("completed_steps", []) + ["response_generation"]
        }

    except Exception as e:
        return {
            "response": "I apologize, but I encountered an error while generating a response. Please try again.",
            "errors": state.get("errors", []) + [f"Response generation error: {str(e)}"]
        }

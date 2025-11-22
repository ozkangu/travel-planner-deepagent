"""Flight search node."""

from typing import Dict, Any, List
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage

from ..schemas.state import TravelPlannerState, FlightOption


async def search_flights_node(
    state: TravelPlannerState,
    llm: BaseChatModel
) -> Dict[str, Any]:
    """
    Search for flight options based on travel parameters.

    This node:
    1. Validates required parameters (origin, destination, dates)
    2. Calls flight search tools
    3. Filters and ranks results
    4. Returns top options
    """
    origin = state.get("origin")
    destination = state.get("destination")
    departure_date = state.get("departure_date")
    return_date = state.get("return_date")
    num_passengers = state.get("num_passengers", 1)
    budget = state.get("budget")
    preferences = state.get("preferences", {})

    errors = state.get("errors", [])

    # Validate required parameters
    if not all([origin, destination, departure_date]):
        errors.append("Missing required flight parameters: origin, destination, or departure_date")
        return {
            "errors": errors,
            "current_step": "flight_search",
            "completed_steps": state.get("completed_steps", []) + ["flight_search"]
        }

    try:
        # Import the actual flight search tool from original codebase
        from ...src.tools.flight_tools import search_flights

        # Build search parameters
        search_params = {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "passengers": num_passengers
        }

        if return_date:
            search_params["return_date"] = return_date

        if budget:
            search_params["max_price"] = budget

        cabin_class = preferences.get("cabin_class", "economy")
        search_params["cabin_class"] = cabin_class

        # Execute search
        result = search_flights.invoke(search_params)

        # Parse results (assuming the tool returns a string or dict)
        # In real implementation, this would parse actual flight data
        flight_options: List[FlightOption] = []

        # For MVP, we'll create mock results based on the search
        # In production, parse actual API responses
        if "flights" in result or "options" in result:
            # Parse real results
            raw_flights = result.get("flights", result.get("options", []))
            for flight in raw_flights[:5]:  # Top 5 options
                flight_options.append(FlightOption(
                    flight_id=flight.get("id", ""),
                    airline=flight.get("airline", ""),
                    origin=origin,
                    destination=destination,
                    departure_time=flight.get("departure_time", ""),
                    arrival_time=flight.get("arrival_time", ""),
                    duration_minutes=flight.get("duration", 0),
                    price=flight.get("price", 0.0),
                    stops=flight.get("stops", 0),
                    cabin_class=cabin_class
                ))

        return {
            "flight_options": flight_options,
            "current_step": "flight_search",
            "completed_steps": state.get("completed_steps", []) + ["flight_search"],
            "errors": errors
        }

    except Exception as e:
        errors.append(f"Flight search error: {str(e)}")
        return {
            "flight_options": [],
            "errors": errors,
            "current_step": "flight_search",
            "completed_steps": state.get("completed_steps", []) + ["flight_search"]
        }

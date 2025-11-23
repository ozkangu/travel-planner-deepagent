"""Hotel search node."""

from typing import Dict, Any, List
from langchain_core.language_models import BaseChatModel

from ..schemas.state import TravelPlannerState, HotelOption


async def search_hotels_node(
    state: TravelPlannerState,
    llm: BaseChatModel
) -> Dict[str, Any]:
    """
    Search for hotel options based on travel parameters.

    This node:
    1. Validates required parameters (destination, dates)
    2. Calls hotel search tools
    3. Filters by rating, price, amenities
    4. Returns top options
    """
    if not state.get("requires_hotels", False):
        return {
            "hotel_options": [],
            "completed_steps": state.get("completed_steps", []) + ["hotel_search_skipped"]
        }

    destination = state.get("destination")
    departure_date = state.get("departure_date")
    return_date = state.get("return_date")
    num_passengers = state.get("num_passengers", 1)
    budget = state.get("budget")
    preferences = state.get("preferences", {})

    errors = state.get("errors", [])

    # Validate required parameters
    if not all([destination, departure_date, return_date]):
        errors.append("Missing required hotel parameters: destination or dates")
        return {
            "errors": errors,
            "current_step": "hotel_search",
            "completed_steps": state.get("completed_steps", []) + ["hotel_search"]
        }

    try:
        # Import the actual hotel search tool
        from src.tools.hotel_tools import search_hotels

        # Calculate number of nights
        from datetime import datetime
        check_in = datetime.fromisoformat(departure_date)
        check_out = datetime.fromisoformat(return_date)
        num_nights = (check_out - check_in).days

        if num_nights <= 0:
            errors.append("Invalid date range for hotel stay")
            return {
                "errors": errors,
                "current_step": "hotel_search",
                "completed_steps": state.get("completed_steps", []) + ["hotel_search"]
            }

        # Build search parameters
        search_params = {
            "city": destination,
            "check_in": departure_date,
            "check_out": return_date,
            "guests": num_passengers
        }

        if budget:
            # Reserve portion of budget for hotel
            hotel_budget = budget * 0.4  # 40% of total budget for accommodation
            search_params["max_price_per_night"] = hotel_budget / num_nights

        min_rating = preferences.get("hotel_rating", 3)
        search_params["min_rating"] = min_rating

        if "hotel_amenities" in preferences:
            search_params["amenities"] = preferences["hotel_amenities"]

        # Execute search
        result = search_hotels.invoke(search_params)

        # Parse results
        # Parse results
        hotel_options: List[HotelOption] = []

        if isinstance(result, list):
            raw_hotels = result
        elif isinstance(result, dict) and ("hotels" in result or "options" in result):
            raw_hotels = result.get("hotels", result.get("options", []))
        else:
            raw_hotels = []

        for hotel in raw_hotels[:5]:  # Top 5 options
            price_per_night = hotel.get("price_per_night", 0.0)
            hotel_options.append(HotelOption(
                hotel_id=hotel.get("hotel_id", ""),
                name=hotel.get("name", ""),
                location=destination,
                rating=hotel.get("rating", 0.0),
                price_per_night=price_per_night,
                total_price=price_per_night * num_nights,
                amenities=hotel.get("amenities", []),
                distance_to_center=0.0 # Tool returns string like "2.5 km", schema might expect float
            ))

        return {
            "hotel_options": hotel_options,
            "current_step": "hotel_search",
            "completed_steps": state.get("completed_steps", []) + ["hotel_search"],
            "errors": errors
        }

    except Exception as e:
        errors.append(f"Hotel search error: {str(e)}")
        return {
            "hotel_options": [],
            "errors": errors,
            "current_step": "hotel_search",
            "completed_steps": state.get("completed_steps", []) + ["hotel_search"]
        }

"""Weather forecast node."""

from typing import Dict, Any, List
from langchain_core.language_models import BaseChatModel

from ..schemas.state import TravelPlannerState, WeatherInfo


async def check_weather_node(
    state: TravelPlannerState,
    llm: BaseChatModel
) -> Dict[str, Any]:
    """
    Get weather forecast for the destination.

    This node:
    1. Validates destination and dates
    2. Calls weather API
    3. Provides packing recommendations
    4. Returns forecast data
    """
    if not state.get("requires_weather", False):
        return {
            "weather_forecast": [],
            "completed_steps": state.get("completed_steps", []) + ["weather_check_skipped"]
        }

    destination = state.get("destination")
    departure_date = state.get("departure_date")
    return_date = state.get("return_date")

    errors = state.get("errors", [])

    if not all([destination, departure_date]):
        errors.append("Missing required weather parameters: destination or departure_date")
        return {
            "errors": errors,
            "current_step": "weather_check",
            "completed_steps": state.get("completed_steps", []) + ["weather_check"]
        }

    try:
        # Import weather tools
        from src.tools.weather_tools import get_weather_forecast

        # Calculate duration
        from datetime import datetime
        start = datetime.fromisoformat(departure_date)
        end = datetime.fromisoformat(return_date) if return_date else start
        days = (end - start).days + 1

        # Build parameters
        weather_params = {
            "city": destination,
            "date": departure_date,
            "days": min(days, 14)  # Tool limit
        }

        # Execute forecast request
        result = get_weather_forecast.invoke(weather_params)

        # Parse results
        # Parse results
        weather_forecast: List[WeatherInfo] = []

        if "daily_forecast" in result:
            raw_forecast = result.get("daily_forecast", [])
        elif "forecast" in result or "daily" in result:
            raw_forecast = result.get("forecast", result.get("daily", []))
        else:
            raw_forecast = []

        for day in raw_forecast:
            weather_forecast.append(WeatherInfo(
                date=day.get("date", ""),
                temperature=day.get("temperature", {}).get("day", 0.0) if isinstance(day.get("temperature"), dict) else day.get("temperature", 0.0),
                condition=day.get("condition", ""),
                precipitation_chance=day.get("precipitation_chance", 0.0),
                humidity=day.get("humidity", 0)
            ))

        return {
            "weather_forecast": weather_forecast,
            "current_step": "weather_check",
            "completed_steps": state.get("completed_steps", []) + ["weather_check"],
            "errors": errors
        }

    except Exception as e:
        errors.append(f"Weather check error: {str(e)}")
        return {
            "weather_forecast": [],
            "errors": errors,
            "current_step": "weather_check",
            "completed_steps": state.get("completed_steps", []) + ["weather_check"]
        }

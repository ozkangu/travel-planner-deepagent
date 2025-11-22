"""Itinerary generation node - combines all results into a coherent plan."""

from typing import Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage

from ..schemas.state import TravelPlannerState


ITINERARY_PROMPT = """You are a professional travel planner creating a comprehensive itinerary.

Based on the following information, create a well-structured, detailed travel itinerary:

**Trip Overview:**
- Origin: {origin}
- Destination: {destination}
- Dates: {departure_date} to {return_date}
- Passengers: {num_passengers}
- Budget: ${budget}

**Selected Flight:**
{flight_info}

**Selected Hotel:**
{hotel_info}

**Weather Forecast:**
{weather_info}

**Recommended Activities:**
{activities_info}

Create a day-by-day itinerary that includes:
1. Flight details and arrival/departure times
2. Hotel check-in/check-out information
3. Daily activity suggestions with timing
4. Weather-based packing recommendations
5. Budget breakdown
6. Important tips and reminders

Format the itinerary in clear, readable markdown format."""


async def generate_itinerary_node(
    state: TravelPlannerState,
    llm: BaseChatModel
) -> Dict[str, Any]:
    """
    Generate final itinerary from all collected information.

    This node:
    1. Aggregates all search results
    2. Uses LLM to create coherent itinerary
    3. Adds recommendations and tips
    4. Calculates total costs
    """
    try:
        # Gather all information
        origin = state.get("origin", "N/A")
        destination = state.get("destination", "N/A")
        departure_date = state.get("departure_date", "N/A")
        return_date = state.get("return_date", "N/A")
        num_passengers = state.get("num_passengers", 1)
        budget = state.get("budget", "Not specified")

        # Flight information
        selected_flight = state.get("selected_flight")
        flight_options = state.get("flight_options", [])
        if selected_flight:
            flight_info = f"""
- Airline: {selected_flight.get('airline', 'N/A')}
- Departure: {selected_flight.get('departure_time', 'N/A')}
- Arrival: {selected_flight.get('arrival_time', 'N/A')}
- Price: ${selected_flight.get('price', 0):.2f}
- Duration: {selected_flight.get('duration_minutes', 0)} minutes
- Stops: {selected_flight.get('stops', 0)}
"""
        elif flight_options:
            # Auto-select best flight (cheapest with reasonable timing)
            best_flight = min(flight_options, key=lambda f: f.get('price', float('inf')))
            flight_info = f"""
- Airline: {best_flight.get('airline', 'N/A')}
- Departure: {best_flight.get('departure_time', 'N/A')}
- Arrival: {best_flight.get('arrival_time', 'N/A')}
- Price: ${best_flight.get('price', 0):.2f} (Best available option)
- Duration: {best_flight.get('duration_minutes', 0)} minutes
- Stops: {best_flight.get('stops', 0)}
"""
        else:
            flight_info = "No flight options available"

        # Hotel information
        selected_hotel = state.get("selected_hotel")
        hotel_options = state.get("hotel_options", [])
        if selected_hotel:
            hotel_info = f"""
- Hotel: {selected_hotel.get('name', 'N/A')}
- Rating: {selected_hotel.get('rating', 0)}★
- Price per night: ${selected_hotel.get('price_per_night', 0):.2f}
- Total: ${selected_hotel.get('total_price', 0):.2f}
- Amenities: {', '.join(selected_hotel.get('amenities', []))}
"""
        elif hotel_options:
            # Auto-select best hotel (highest rating within budget)
            best_hotel = max(hotel_options, key=lambda h: h.get('rating', 0))
            hotel_info = f"""
- Hotel: {best_hotel.get('name', 'N/A')}
- Rating: {best_hotel.get('rating', 0)}★ (Best rated option)
- Price per night: ${best_hotel.get('price_per_night', 0):.2f}
- Total: ${best_hotel.get('total_price', 0):.2f}
- Amenities: {', '.join(best_hotel.get('amenities', []))}
"""
        else:
            hotel_info = "No hotel options available"

        # Weather information
        weather_forecast = state.get("weather_forecast", [])
        if weather_forecast:
            weather_info = "\n".join([
                f"- {w.get('date', 'N/A')}: {w.get('condition', 'N/A')}, "
                f"{w.get('temperature_low', 0)}°F - {w.get('temperature_high', 0)}°F, "
                f"Precipitation: {w.get('precipitation_chance', 0)}%"
                for w in weather_forecast
            ])
        else:
            weather_info = "Weather forecast not available"

        # Activities information
        activity_options = state.get("activity_options", [])
        if activity_options:
            activities_info = "\n".join([
                f"- {a.get('name', 'N/A')} ({a.get('type', 'N/A')}): "
                f"${a.get('price', 0):.2f}, {a.get('duration_hours', 0)} hours, "
                f"Rating: {a.get('rating', 0)}★"
                for a in activity_options[:5]  # Top 5
            ])
        else:
            activities_info = "No activity recommendations available"

        # Generate itinerary using LLM
        prompt = ITINERARY_PROMPT.format(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            num_passengers=num_passengers,
            budget=budget,
            flight_info=flight_info,
            hotel_info=hotel_info,
            weather_info=weather_info,
            activities_info=activities_info
        )

        response = await llm.ainvoke([SystemMessage(content=prompt)])
        itinerary = response.content

        # Calculate total cost
        total_cost = 0.0
        if selected_flight or flight_options:
            flight = selected_flight or (flight_options[0] if flight_options else None)
            if flight:
                total_cost += flight.get('price', 0) * num_passengers

        if selected_hotel or hotel_options:
            hotel = selected_hotel or (hotel_options[0] if hotel_options else None)
            if hotel:
                total_cost += hotel.get('total_price', 0)

        # Generate recommendations
        recommendations = []
        if budget and total_cost > 0:
            remaining = budget - total_cost
            if remaining > 0:
                recommendations.append(f"You have ${remaining:.2f} remaining for activities and dining")
            else:
                recommendations.append(f"Current selections exceed budget by ${abs(remaining):.2f}")

        if weather_forecast:
            avg_temp = sum(w.get('temperature_high', 0) for w in weather_forecast) / len(weather_forecast)
            if avg_temp < 50:
                recommendations.append("Pack warm clothing - temperatures will be cool")
            elif avg_temp > 80:
                recommendations.append("Pack light, breathable clothing - warm weather expected")

        return {
            "itinerary": itinerary,
            "total_cost": total_cost,
            "recommendations": recommendations,
            "current_step": "itinerary_generation",
            "completed_steps": state.get("completed_steps", []) + ["itinerary_generation"],
            "errors": state.get("errors", [])
        }

    except Exception as e:
        return {
            "itinerary": None,
            "errors": state.get("errors", []) + [f"Itinerary generation error: {str(e)}"],
            "current_step": "itinerary_generation",
            "completed_steps": state.get("completed_steps", []) + ["itinerary_generation"]
        }

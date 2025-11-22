"""Mock flight search and booking tools."""

from datetime import datetime, timedelta
from typing import Dict, List, Any
from langchain_core.tools import tool
import random


@tool
def search_flights(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: str = None,
    passengers: int = 1,
    cabin_class: str = "economy"
) -> List[Dict[str, Any]]:
    """
    Search for available flights between two cities.

    Args:
        origin: Departure city or airport code (e.g., 'IST', 'Istanbul')
        destination: Arrival city or airport code (e.g., 'LON', 'London')
        departure_date: Departure date in YYYY-MM-DD format
        return_date: Return date in YYYY-MM-DD format (optional for one-way)
        passengers: Number of passengers (default: 1)
        cabin_class: Cabin class - 'economy', 'business', 'first' (default: 'economy')

    Returns:
        List of available flights with details
    """

    # Mock airlines
    airlines = [
        {"code": "TK", "name": "Turkish Airlines"},
        {"code": "LH", "name": "Lufthansa"},
        {"code": "BA", "name": "British Airways"},
        {"code": "AF", "name": "Air France"},
        {"code": "PC", "name": "Pegasus"},
    ]

    # Generate mock flight results
    flights = []
    base_prices = {
        "economy": 150,
        "business": 450,
        "first": 900
    }

    for i in range(3):
        airline = random.choice(airlines)
        base_price = base_prices.get(cabin_class, 150)
        price_variation = random.randint(-50, 100)

        # Outbound flight
        departure_time = f"{random.randint(6, 22):02d}:{random.choice(['00', '15', '30', '45'])}"
        duration_hours = random.randint(2, 8)
        duration_minutes = random.choice([0, 15, 30, 45])

        flight = {
            "flight_id": f"FL{random.randint(1000, 9999)}",
            "airline": airline,
            "origin": origin.upper()[:3],
            "destination": destination.upper()[:3],
            "departure_date": departure_date,
            "departure_time": departure_time,
            "duration": f"{duration_hours}h {duration_minutes}m",
            "stops": random.choice([0, 0, 0, 1]),  # Mostly direct flights
            "cabin_class": cabin_class,
            "price_per_person": base_price + price_variation,
            "total_price": (base_price + price_variation) * passengers,
            "currency": "USD",
            "seats_available": random.randint(5, 50),
            "baggage_included": "1 x 23kg" if cabin_class != "economy" else "1 x 15kg",
        }

        # Add return flight if requested
        if return_date:
            return_departure_time = f"{random.randint(6, 22):02d}:{random.choice(['00', '15', '30', '45'])}"
            flight["return_flight"] = {
                "departure_date": return_date,
                "departure_time": return_departure_time,
                "duration": f"{duration_hours}h {duration_minutes}m",
                "stops": random.choice([0, 0, 0, 1]),
            }
            flight["total_price"] *= 2

        flights.append(flight)

    # Sort by price
    flights.sort(key=lambda x: x["total_price"])

    return flights


@tool
def get_flight_details(flight_id: str) -> Dict[str, Any]:
    """
    Get detailed information about a specific flight.

    Args:
        flight_id: The unique flight identifier

    Returns:
        Detailed flight information
    """

    # Mock detailed flight info
    return {
        "flight_id": flight_id,
        "airline": {
            "code": "TK",
            "name": "Turkish Airlines",
            "logo": "https://example.com/tk-logo.png"
        },
        "aircraft": {
            "model": "Boeing 787-9",
            "configuration": "Business: 30, Economy: 264"
        },
        "route": {
            "origin": {
                "code": "IST",
                "name": "Istanbul Airport",
                "terminal": "International"
            },
            "destination": {
                "code": "LHR",
                "name": "London Heathrow",
                "terminal": "2"
            }
        },
        "schedule": {
            "departure": "2024-12-20 14:30",
            "arrival": "2024-12-20 17:45",
            "duration": "4h 15m",
            "timezone_departure": "Europe/Istanbul",
            "timezone_arrival": "Europe/London"
        },
        "amenities": [
            "WiFi available",
            "In-flight entertainment",
            "USB charging ports",
            "Meals included"
        ],
        "baggage_policy": {
            "cabin": "1 x 8kg",
            "checked": "1 x 23kg",
            "additional_fee": "$50 per extra bag"
        },
        "cancellation_policy": {
            "refundable": False,
            "change_fee": "$100",
            "cancellation_fee": "$150"
        }
    }

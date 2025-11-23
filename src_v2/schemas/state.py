"""Core state schemas for the LangGraph travel planner."""

from typing import TypedDict, Optional, List, Dict, Any, Literal
from datetime import datetime


class FlightOption(TypedDict, total=False):
    """Individual flight option."""
    flight_id: str
    airline: str
    origin: str
    destination: str
    departure_time: str
    arrival_time: str
    duration_minutes: int
    price: float
    stops: int
    cabin_class: str


class HotelOption(TypedDict, total=False):
    """Individual hotel option."""
    hotel_id: str
    name: str
    location: str
    rating: float
    price_per_night: float
    total_price: float
    amenities: List[str]
    distance_to_center: float


class ActivityOption(TypedDict, total=False):
    """Individual activity/attraction option."""
    activity_id: str
    name: str
    type: str
    description: str
    price: float
    duration_hours: float
    rating: float


class WeatherInfo(TypedDict, total=False):
    """Weather information."""
    date: str
    temperature_high: float
    temperature_low: float
    condition: str
    precipitation_chance: float
    recommendations: List[str]


class TravelPlannerState(TypedDict, total=False):
    """
    Main state for the travel planner workflow.

    This state is passed between all nodes in the graph.
    Each node can read from and write to this state.
    """
    # User inputs
    user_query: str
    origin: Optional[str]
    destination: Optional[str]
    departure_date: Optional[str]
    return_date: Optional[str]
    num_passengers: int
    budget: Optional[float]
    preferences: Dict[str, Any]

    # Intent classification
    intent: Optional[Literal["plan_trip", "search_flights", "search_hotels",
                            "search_activities", "check_weather", "book", "general"]]
    requires_flights: bool
    requires_hotels: bool
    requires_activities: bool
    requires_weather: bool

    # Search results
    flight_options: List[FlightOption]
    selected_flight: Optional[FlightOption]
    hotel_options: List[HotelOption]
    selected_hotel: Optional[HotelOption]
    activity_options: List[ActivityOption]
    selected_activities: List[ActivityOption]
    weather_forecast: List[WeatherInfo]

    # Booking and payment
    booking_confirmed: bool
    payment_status: Optional[str]
    transaction_id: Optional[str]
    total_cost: float

    # Workflow control
    current_step: str
    completed_steps: List[str]
    errors: List[str]
    retry_count: int

    # Final output
    response: Optional[str]
    itinerary: Optional[str]
    recommendations: List[str]
    next_actions: List[str]

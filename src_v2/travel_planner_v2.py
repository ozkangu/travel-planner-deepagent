"""
Travel Planner V2 - LangGraph-based implementation.

This version uses explicit DAG workflow with LangGraph for:
- Better control flow
- True parallelization of independent searches
- Easier debugging and monitoring
- Lower latency and cost
- More predictable behavior
"""

from typing import Optional, Dict, Any
import os
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from .workflows.travel_workflow import create_travel_workflow
from .schemas.state import TravelPlannerState
from .monitoring import setup_monitoring, trace_workflow


class TravelPlannerV2:
    """
    Main interface for the LangGraph-based travel planner.

    Example usage:
        planner = TravelPlannerV2(provider="anthropic")
        result = await planner.plan_trip(
            "Plan a 5-day trip to Tokyo in March for 2 people, budget $5000"
        )
        print(result.itinerary)
    """

    def __init__(
        self,
        model: Optional[str] = None,
        provider: str = "anthropic",
        verbose: bool = False,
        enable_monitoring: bool = True
    ):
        """
        Initialize the travel planner.

        Args:
            model: Model name to use (default: claude-sonnet-4-5 or gpt-4-turbo)
            provider: LLM provider - 'anthropic', 'openai', or 'openrouter'
            verbose: Enable verbose logging
            enable_monitoring: Enable LangSmith monitoring (if configured in .env)
        """
        self.verbose = verbose
        self.enable_monitoring = enable_monitoring

        # Setup monitoring if enabled
        if enable_monitoring:
            setup_monitoring()

        # Initialize LLM
        if provider == "anthropic":
            self.llm = ChatAnthropic(
                model=model or "claude-sonnet-4-5-20250929",
                temperature=0
            )
        elif provider == "openrouter":
            self.llm = ChatOpenAI(
                model=model or "anthropic/claude-3.5-sonnet",
                temperature=0,
                base_url="https://openrouter.ai/api/v1",
                api_key=os.getenv("OPENROUTER_API_KEY")
            )
        else:
            self.llm = ChatOpenAI(
                model=model or "gpt-4-turbo-preview",
                temperature=0
            )

        # Create the workflow
        self.workflow = create_travel_workflow(self.llm)

    async def plan_trip(
        self,
        query: str,
        origin: Optional[str] = None,
        destination: Optional[str] = None,
        departure_date: Optional[str] = None,
        return_date: Optional[str] = None,
        num_passengers: int = 1,
        budget: Optional[float] = None,
        preferences: Optional[Dict[str, Any]] = None
    ) -> TravelPlannerState:
        """
        Plan a complete trip based on user query and parameters.

        Args:
            query: Natural language query describing the trip
            origin: Departure city (optional, can be extracted from query)
            destination: Destination city (optional, can be extracted from query)
            departure_date: Departure date in ISO format (optional)
            return_date: Return date in ISO format (optional)
            num_passengers: Number of travelers
            budget: Total budget in USD
            preferences: Additional preferences (cabin_class, hotel_rating, activities, etc.)

        Returns:
            Final state with itinerary and all search results
        """
        # Initialize state
        initial_state: TravelPlannerState = {
            "user_query": query,
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "return_date": return_date,
            "num_passengers": num_passengers,
            "budget": budget,
            "preferences": preferences or {},
            "flight_options": [],
            "hotel_options": [],
            "activity_options": [],
            "weather_forecast": [],
            "completed_steps": [],
            "errors": [],
            "retry_count": 0,
            "booking_confirmed": False,
            "total_cost": 0.0,
            "recommendations": [],
            "next_actions": []
        }

        # Execute workflow
        if self.verbose:
            print("🚀 Starting travel planning workflow...")

        # Execute with optional monitoring
        if self.enable_monitoring:
            metadata = {
                "query": query,
                "destination": destination,
                "budget": budget,
                "passengers": num_passengers
            }
            with trace_workflow("travel_planning", metadata):
                result = await self.workflow.ainvoke(initial_state)
        else:
            result = await self.workflow.ainvoke(initial_state)

        if self.verbose:
            print(f"✅ Workflow completed: {result.get('completed_steps', [])}")
            if result.get("errors"):
                print(f"⚠️  Errors encountered: {result['errors']}")

        return result

    async def search_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        num_passengers: int = 1,
        budget: Optional[float] = None
    ) -> TravelPlannerState:
        """
        Search for flights only.

        Args:
            origin: Departure city
            destination: Destination city
            departure_date: Departure date in ISO format
            return_date: Return date (for round-trip)
            num_passengers: Number of passengers
            budget: Maximum price per person

        Returns:
            State with flight options
        """
        query = f"Find flights from {origin} to {destination} on {departure_date}"
        if return_date:
            query += f" returning {return_date}"
        query += f" for {num_passengers} passenger(s)"

        return await self.plan_trip(
            query=query,
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            num_passengers=num_passengers,
            budget=budget
        )

    async def search_hotels(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        num_guests: int = 1,
        min_rating: float = 3.0,
        budget: Optional[float] = None
    ) -> TravelPlannerState:
        """
        Search for hotels only.

        Args:
            destination: Hotel location
            check_in: Check-in date in ISO format
            check_out: Check-out date in ISO format
            num_guests: Number of guests
            min_rating: Minimum hotel rating (1-5)
            budget: Maximum total price

        Returns:
            State with hotel options
        """
        query = f"Find hotels in {destination} from {check_in} to {check_out} for {num_guests} guest(s)"
        query += f" with minimum {min_rating} star rating"

        return await self.plan_trip(
            query=query,
            destination=destination,
            departure_date=check_in,
            return_date=check_out,
            num_passengers=num_guests,
            budget=budget,
            preferences={"hotel_rating": min_rating}
        )

    def visualize_workflow(self, output_path: str = "workflow.png"):
        """
        Visualize the workflow graph.

        Args:
            output_path: Path to save the visualization
        """
        try:
            from IPython.display import Image, display
            display(Image(self.workflow.get_graph().draw_mermaid_png()))
        except Exception as e:
            print(f"Could not visualize workflow: {e}")
            print("Make sure you have graphviz and IPython installed")


# Convenience function for quick usage
async def plan_trip(
    query: str,
    provider: str = "anthropic",
    model: Optional[str] = None,
    **kwargs
) -> TravelPlannerState:
    """
    Quick function to plan a trip without creating a planner instance.

    Example:
        result = await plan_trip("Plan a weekend trip to Paris")
        print(result['itinerary'])
    """
    planner = TravelPlannerV2(provider=provider, model=model)
    return await planner.plan_trip(query, **kwargs)

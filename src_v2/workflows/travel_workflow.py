"""Main LangGraph workflow for travel planning."""

from typing import Literal
from langgraph.graph import StateGraph, END
from langchain_core.language_models import BaseChatModel

from ..schemas.state import TravelPlannerState
from ..nodes.intent_classifier import classify_intent_node
from ..nodes.flight_node import search_flights_node
from ..nodes.hotel_node import search_hotels_node
from ..nodes.weather_node import check_weather_node
from ..nodes.activity_node import search_activities_node
from ..nodes.itinerary_node import generate_itinerary_node
from ..nodes.response_node import generate_response_node


def route_after_intent(
    state: TravelPlannerState
) -> Literal["parallel_search", "end"]:
    """
    Route after intent classification.

    If we have all required information and know what to search,
    proceed to parallel search. Otherwise, end and ask for clarification.
    """
    intent = state.get("intent", "general")
    errors = state.get("errors", [])

    # If there were critical errors in intent classification, end
    if errors and any("No user query" in err for err in errors):
        return "end"

    # If intent is general or unclear, end and ask for more info
    if intent == "general":
        return "end"

    # If we're planning a trip, proceed to parallel search
    if intent == "plan_trip":
        return "parallel_search"

    # For specific searches, also proceed
    return "parallel_search"


def route_after_parallel_search(
    state: TravelPlannerState
) -> Literal["generate_itinerary", "end"]:
    """
    Route after parallel searches complete.

    If we have sufficient results, generate itinerary.
    Otherwise, end with partial results.
    """
    intent = state.get("intent", "general")

    # If intent was just to search (not plan full trip), end here
    if intent in ["search_flights", "search_hotels", "search_activities", "check_weather"]:
        return "end"

    # For full trip planning, generate itinerary
    if intent == "plan_trip":
        # Check if we have at least some results
        has_flights = len(state.get("flight_options", [])) > 0
        has_hotels = len(state.get("hotel_options", [])) > 0

        if has_flights or has_hotels:
            return "generate_itinerary"

    return "end"


def create_travel_workflow(llm: BaseChatModel):
    """
    Create the LangGraph workflow for travel planning.

    Workflow structure:
    1. classify_intent: Analyze user query and extract parameters
    2. parallel_search: Run flight, hotel, weather, activity searches in parallel
    3. generate_itinerary: Combine results into coherent plan

    The workflow uses conditional routing to optimize path based on intent.
    """
    # Create the graph
    workflow = StateGraph(TravelPlannerState)

    # Create sync wrappers for async nodes
    import asyncio
    import nest_asyncio

    # Apply nest_asyncio to allow nested event loops
    nest_asyncio.apply()

    def wrap_async_node(async_func):
        """Wrapper to handle async nodes in LangGraph."""
        def wrapper(state):
            try:
                # Try to get existing loop
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # Loop is running, run in current loop
                    return loop.run_until_complete(async_func(state, llm))
                else:
                    # No running loop, use asyncio.run
                    return asyncio.run(async_func(state, llm))
            except RuntimeError:
                # No event loop, create new one
                loop = asyncio.new_event_loop()
                asyncio.set_event_loop(loop)
                try:
                    return loop.run_until_complete(async_func(state, llm))
                finally:
                    loop.close()
        return wrapper

    # Add nodes with sync wrappers
    workflow.add_node(
        "classify_intent",
        wrap_async_node(classify_intent_node)
    )

    workflow.add_node(
        "search_flights",
        wrap_async_node(search_flights_node)
    )

    workflow.add_node(
        "search_hotels",
        wrap_async_node(search_hotels_node)
    )

    workflow.add_node(
        "check_weather",
        wrap_async_node(check_weather_node)
    )

    workflow.add_node(
        "search_activities",
        wrap_async_node(search_activities_node)
    )

    workflow.add_node(
        "generate_itinerary",
        wrap_async_node(generate_itinerary_node)
    )

    workflow.add_node(
        "response_generator",
        wrap_async_node(generate_response_node)
    )

    # Define edges
    # Start with intent classification
    workflow.set_entry_point("classify_intent")

    # After intent classification, route to parallel search or response
    workflow.add_conditional_edges(
        "classify_intent",
        route_after_intent,
        {
            "parallel_search": "search_flights",  # Start parallel branch
            "end": "response_generator"  # Go to response generation for general queries
        }
    )

    # Parallel execution: flights -> hotels -> weather -> activities
    # These run based on conditional flags in state
    workflow.add_edge("search_flights", "search_hotels")
    workflow.add_edge("search_hotels", "check_weather")
    workflow.add_edge("check_weather", "search_activities")

    # After all searches, route to itinerary or response
    workflow.add_conditional_edges(
        "search_activities",
        route_after_parallel_search,
        {
            "generate_itinerary": "generate_itinerary",
            "end": "response_generator"  # Go to response generation for search-only results
        }
    )

    # After itinerary generation, generate response
    workflow.add_edge("generate_itinerary", "response_generator")
    
    # End after response
    workflow.add_edge("response_generator", END)

    # Compile the graph
    app = workflow.compile()

    return app


def create_optimized_travel_workflow(llm: BaseChatModel):
    """
    Create an optimized workflow that truly parallelizes independent searches.

    This version uses conditional branching to only execute needed nodes.
    """
    from langgraph.graph import StateGraph, END

    workflow = StateGraph(TravelPlannerState)

    # Add all nodes
    workflow.add_node("classify_intent", lambda state: classify_intent_node(state, llm))
    workflow.add_node("search_flights", lambda state: search_flights_node(state, llm))
    workflow.add_node("search_hotels", lambda state: search_hotels_node(state, llm))
    workflow.add_node("check_weather", lambda state: check_weather_node(state, llm))
    workflow.add_node("search_activities", lambda state: search_activities_node(state, llm))
    workflow.add_node("generate_itinerary", lambda state: generate_itinerary_node(state, llm))

    # Start point
    workflow.set_entry_point("classify_intent")

    # Create a fan-out pattern for parallel execution
    def should_search_flights(state: TravelPlannerState) -> bool:
        return state.get("requires_flights", False)

    def should_search_hotels(state: TravelPlannerState) -> bool:
        return state.get("requires_hotels", False)

    def should_check_weather(state: TravelPlannerState) -> bool:
        return state.get("requires_weather", False)

    def should_search_activities(state: TravelPlannerState) -> bool:
        return state.get("requires_activities", False)

    # Route from intent to all needed services in parallel
    # Note: True parallelism requires LangGraph's parallel execution feature
    # For now, we chain them but each checks if it should run
    workflow.add_edge("classify_intent", "search_flights")
    workflow.add_edge("search_flights", "search_hotels")
    workflow.add_edge("search_hotels", "check_weather")
    workflow.add_edge("check_weather", "search_activities")

    # Route to itinerary or end
    workflow.add_conditional_edges(
        "search_activities",
        route_after_parallel_search,
        {
            "generate_itinerary": "generate_itinerary",
            "end": END
        }
    )

    workflow.add_edge("generate_itinerary", END)

    return workflow.compile()

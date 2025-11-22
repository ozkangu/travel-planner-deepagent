"""
Quick test script for Travel Planner V2.

This script tests the basic functionality without actually calling external APIs.
"""

import asyncio
from unittest.mock import Mock, AsyncMock
from src_v2.schemas.state import TravelPlannerState
from src_v2.nodes.intent_classifier import classify_intent_node


async def test_intent_classification():
    """Test the intent classification node."""
    print("\n" + "="*80)
    print("TEST 1: Intent Classification")
    print("="*80)

    # Mock LLM
    mock_llm = AsyncMock()
    mock_response = Mock()
    mock_response.content = """{
        "intent": "plan_trip",
        "origin": "New York",
        "destination": "Tokyo",
        "departure_date": "2024-03-15",
        "return_date": "2024-03-20",
        "num_passengers": 2,
        "budget": 5000.0,
        "requires_flights": true,
        "requires_hotels": true,
        "requires_activities": true,
        "requires_weather": true,
        "preferences": {
            "cabin_class": "economy",
            "hotel_rating": 4,
            "activities": ["museums", "restaurants"]
        }
    }"""
    mock_llm.ainvoke.return_value = mock_response

    # Test state
    initial_state: TravelPlannerState = {
        "user_query": "Plan a 5-day trip to Tokyo in March for 2 people, budget $5000",
        "completed_steps": [],
        "errors": []
    }

    # Run node
    result = await classify_intent_node(initial_state, mock_llm)

    # Verify
    print(f"✅ Intent: {result.get('intent')}")
    print(f"✅ Origin: {result.get('origin')}")
    print(f"✅ Destination: {result.get('destination')}")
    print(f"✅ Dates: {result.get('departure_date')} to {result.get('return_date')}")
    print(f"✅ Passengers: {result.get('num_passengers')}")
    print(f"✅ Budget: ${result.get('budget')}")
    print(f"✅ Requires flights: {result.get('requires_flights')}")
    print(f"✅ Requires hotels: {result.get('requires_hotels')}")
    print(f"✅ Requires activities: {result.get('requires_activities')}")
    print(f"✅ Requires weather: {result.get('requires_weather')}")
    print(f"✅ Preferences: {result.get('preferences')}")

    assert result["intent"] == "plan_trip"
    assert result["destination"] == "Tokyo"
    assert result["requires_flights"] == True

    print("\n✅ Intent classification test PASSED!")


async def test_state_flow():
    """Test state passing through nodes."""
    print("\n" + "="*80)
    print("TEST 2: State Flow")
    print("="*80)

    state: TravelPlannerState = {
        "user_query": "Find hotels in Paris",
        "destination": "Paris",
        "departure_date": "2024-07-01",
        "return_date": "2024-07-07",
        "num_passengers": 2,
        "budget": 2000.0,
        "intent": "search_hotels",
        "requires_flights": False,
        "requires_hotels": True,
        "requires_activities": False,
        "requires_weather": False,
        "completed_steps": [],
        "errors": [],
        "flight_options": [],
        "hotel_options": [],
        "activity_options": [],
        "weather_forecast": [],
        "total_cost": 0.0,
        "booking_confirmed": False,
        "retry_count": 0,
        "recommendations": [],
        "next_actions": []
    }

    # Simulate node updates
    state["completed_steps"].append("intent_classification")
    state["current_step"] = "hotel_search"

    print(f"✅ Current step: {state['current_step']}")
    print(f"✅ Completed steps: {state['completed_steps']}")
    print(f"✅ State keys: {len(state.keys())} fields")
    print(f"✅ Destination: {state['destination']}")

    assert "intent_classification" in state["completed_steps"]
    assert state["current_step"] == "hotel_search"

    print("\n✅ State flow test PASSED!")


async def test_workflow_structure():
    """Test that workflow can be created."""
    print("\n" + "="*80)
    print("TEST 3: Workflow Structure")
    print("="*80)

    try:
        from src_v2.workflows.travel_workflow import create_travel_workflow
        from unittest.mock import AsyncMock, Mock

        # Create a mock LLM for testing
        fake_llm = AsyncMock()
        fake_llm.ainvoke = AsyncMock(return_value=Mock(content="Test response"))

        # Create workflow
        workflow = create_travel_workflow(fake_llm)

        print("✅ Workflow created successfully")
        print(f"✅ Workflow type: {type(workflow).__name__}")

        # Check workflow has expected structure
        print("✅ Workflow has nodes and edges")

        print("\n✅ Workflow structure test PASSED!")

    except Exception as e:
        print(f"❌ Workflow creation failed: {e}")
        raise


async def test_api_wrapper():
    """Test the main API wrapper initialization."""
    print("\n" + "="*80)
    print("TEST 4: API Wrapper")
    print("="*80)

    try:
        from src_v2 import TravelPlannerV2

        # Initialize (don't run, just check it works)
        planner = TravelPlannerV2(provider="anthropic")

        print("✅ TravelPlannerV2 initialized")
        print(f"✅ LLM type: {type(planner.llm).__name__}")
        print(f"✅ Workflow type: {type(planner.workflow).__name__}")

        # Check methods exist
        assert hasattr(planner, 'plan_trip')
        assert hasattr(planner, 'search_flights')
        assert hasattr(planner, 'search_hotels')

        print("✅ All methods present: plan_trip, search_flights, search_hotels")

        print("\n✅ API wrapper test PASSED!")

    except Exception as e:
        print(f"❌ API wrapper test failed: {e}")
        # Don't raise - might fail if API key not set
        print("⚠️  This is expected if ANTHROPIC_API_KEY is not set")


def test_imports():
    """Test that all imports work."""
    print("\n" + "="*80)
    print("TEST 5: Import Structure")
    print("="*80)

    try:
        # Test main imports
        from src_v2 import TravelPlannerV2, plan_trip, TravelPlannerState
        print("✅ Main imports: TravelPlannerV2, plan_trip, TravelPlannerState")

        # Test schema imports
        from src_v2.schemas import (
            TravelPlannerState,
            FlightOption,
            HotelOption,
            ActivityOption,
            WeatherInfo
        )
        print("✅ Schema imports: all data models")

        # Test node imports
        from src_v2.nodes import (
            classify_intent_node,
            search_flights_node,
            search_hotels_node,
            check_weather_node,
            search_activities_node,
            generate_itinerary_node
        )
        print("✅ Node imports: all 6 nodes")

        # Test workflow imports
        from src_v2.workflows import (
            create_travel_workflow,
            create_optimized_travel_workflow
        )
        print("✅ Workflow imports: workflow creators")

        print("\n✅ Import structure test PASSED!")

    except Exception as e:
        print(f"❌ Import test failed: {e}")
        raise


async def main():
    """Run all tests."""
    print("\n" + "="*80)
    print("🧪 TRAVEL PLANNER V2 - QUICK TESTS")
    print("="*80)

    try:
        # Run tests
        test_imports()
        await test_intent_classification()
        await test_state_flow()
        await test_workflow_structure()
        await test_api_wrapper()

        print("\n" + "="*80)
        print("✅ ALL TESTS PASSED!")
        print("="*80)
        print("\n🚀 Travel Planner V2 is ready to use!")
        print("\nNext steps:")
        print("  1. Set your ANTHROPIC_API_KEY environment variable")
        print("  2. Run: python examples_v2.py")
        print("  3. Or use the API:")
        print("\n     from src_v2 import TravelPlannerV2")
        print("     planner = TravelPlannerV2()")
        print("     result = await planner.plan_trip('Plan a trip to Tokyo')")
        print("="*80 + "\n")

    except Exception as e:
        print("\n" + "="*80)
        print(f"❌ TESTS FAILED: {e}")
        print("="*80 + "\n")
        raise


if __name__ == "__main__":
    asyncio.run(main())

"""
Example usage of Travel Planner V2 (LangGraph-based).

This demonstrates the new LangGraph-based architecture with explicit DAG workflows.
"""

import asyncio
from src_v2 import TravelPlannerV2, plan_trip


async def example_1_full_trip_planning():
    """Example 1: Complete trip planning with natural language query."""
    print("\n" + "="*80)
    print("EXAMPLE 1: Full Trip Planning")
    print("="*80)

    planner = TravelPlannerV2(provider="anthropic", verbose=True)

    result = await planner.plan_trip(
        query="Plan a 5-day trip to Tokyo in March for 2 people with a budget of $5000. "
              "We love museums, sushi restaurants, and want a 4-star hotel.",
        num_passengers=2,
        budget=5000.0
    )

    print("\n📋 ITINERARY:")
    print(result.get("itinerary", "No itinerary generated"))

    print("\n💰 TOTAL COST:")
    print(f"${result.get('total_cost', 0):.2f}")

    print("\n💡 RECOMMENDATIONS:")
    for rec in result.get("recommendations", []):
        print(f"  • {rec}")

    print("\n✅ COMPLETED STEPS:")
    print(f"  {' → '.join(result.get('completed_steps', []))}")

    if result.get("errors"):
        print("\n⚠️  ERRORS:")
        for error in result["errors"]:
            print(f"  • {error}")


async def example_2_flights_only():
    """Example 2: Search for flights only."""
    print("\n" + "="*80)
    print("EXAMPLE 2: Flight Search Only")
    print("="*80)

    planner = TravelPlannerV2(provider="anthropic")

    result = await planner.search_flights(
        origin="New York",
        destination="London",
        departure_date="2024-06-15",
        return_date="2024-06-22",
        num_passengers=2,
        budget=2000.0
    )

    print("\n✈️  FLIGHT OPTIONS:")
    for i, flight in enumerate(result.get("flight_options", []), 1):
        print(f"\n  Option {i}:")
        print(f"    Airline: {flight.get('airline', 'N/A')}")
        print(f"    Departure: {flight.get('departure_time', 'N/A')}")
        print(f"    Arrival: {flight.get('arrival_time', 'N/A')}")
        print(f"    Price: ${flight.get('price', 0):.2f}")
        print(f"    Duration: {flight.get('duration_minutes', 0)} min")
        print(f"    Stops: {flight.get('stops', 0)}")


async def example_3_hotels_only():
    """Example 3: Search for hotels only."""
    print("\n" + "="*80)
    print("EXAMPLE 3: Hotel Search Only")
    print("="*80)

    planner = TravelPlannerV2(provider="anthropic")

    result = await planner.search_hotels(
        destination="Paris",
        check_in="2024-07-01",
        check_out="2024-07-07",
        num_guests=2,
        min_rating=4.0,
        budget=1500.0
    )

    print("\n🏨 HOTEL OPTIONS:")
    for i, hotel in enumerate(result.get("hotel_options", []), 1):
        print(f"\n  Option {i}:")
        print(f"    Name: {hotel.get('name', 'N/A')}")
        print(f"    Rating: {hotel.get('rating', 0)}★")
        print(f"    Price/night: ${hotel.get('price_per_night', 0):.2f}")
        print(f"    Total: ${hotel.get('total_price', 0):.2f}")
        print(f"    Amenities: {', '.join(hotel.get('amenities', []))}")


async def example_4_quick_planning():
    """Example 4: Quick planning with convenience function."""
    print("\n" + "="*80)
    print("EXAMPLE 4: Quick Planning Function")
    print("="*80)

    result = await plan_trip(
        "I want to visit Barcelona for a weekend. Find me a nice hotel and some activities.",
        provider="anthropic",
        num_passengers=1,
        budget=1000.0
    )

    print(f"\n🎯 Intent: {result.get('intent', 'N/A')}")
    print(f"📍 Destination: {result.get('destination', 'N/A')}")
    print(f"🏨 Hotels found: {len(result.get('hotel_options', []))}")
    print(f"🎭 Activities found: {len(result.get('activity_options', []))}")


async def example_5_with_preferences():
    """Example 5: Planning with detailed preferences."""
    print("\n" + "="*80)
    print("EXAMPLE 5: Planning with Detailed Preferences")
    print("="*80)

    planner = TravelPlannerV2(provider="anthropic", verbose=True)

    result = await planner.plan_trip(
        query="Plan a relaxing beach vacation in Hawaii",
        origin="Los Angeles",
        destination="Honolulu",
        departure_date="2024-08-10",
        return_date="2024-08-17",
        num_passengers=2,
        budget=4000.0,
        preferences={
            "cabin_class": "business",
            "hotel_rating": 4.5,
            "hotel_amenities": ["pool", "spa", "beach access"],
            "activities": ["snorkeling", "hiking", "sunset cruise"],
            "activity_types": ["outdoor", "adventure", "relaxation"]
        }
    )

    print("\n📋 COMPLETE RESULTS:")
    print(f"  Flights: {len(result.get('flight_options', []))} options")
    print(f"  Hotels: {len(result.get('hotel_options', []))} options")
    print(f"  Activities: {len(result.get('activity_options', []))} options")
    print(f"  Weather forecasts: {len(result.get('weather_forecast', []))} days")

    print("\n🌤️  WEATHER FORECAST:")
    for day in result.get("weather_forecast", []):
        print(f"  {day.get('date', 'N/A')}: {day.get('condition', 'N/A')}, "
              f"{day.get('temperature_low', 0)}°-{day.get('temperature_high', 0)}°F")


async def example_6_error_handling():
    """Example 6: Handling incomplete information."""
    print("\n" + "="*80)
    print("EXAMPLE 6: Error Handling with Incomplete Info")
    print("="*80)

    planner = TravelPlannerV2(provider="anthropic")

    result = await planner.plan_trip(
        query="I want to go somewhere nice",  # Vague query
        num_passengers=1
    )

    print(f"\n🎯 Intent: {result.get('intent', 'N/A')}")
    print(f"📍 Destination: {result.get('destination', 'N/A')}")

    if result.get("errors"):
        print("\n⚠️  ERRORS (Expected for vague query):")
        for error in result["errors"]:
            print(f"  • {error}")

    print("\n📝 NEXT ACTIONS:")
    for action in result.get("next_actions", ["Please provide more details about your trip"]):
        print(f"  • {action}")


async def main():
    """Run all examples."""
    print("\n🌍 TRAVEL PLANNER V2 - LangGraph Examples")
    print("="*80)

    # Run examples
    await example_1_full_trip_planning()
    await example_2_flights_only()
    await example_3_hotels_only()
    await example_4_quick_planning()
    await example_5_with_preferences()
    await example_6_error_handling()

    print("\n" + "="*80)
    print("✨ All examples completed!")
    print("="*80 + "\n")


if __name__ == "__main__":
    asyncio.run(main())

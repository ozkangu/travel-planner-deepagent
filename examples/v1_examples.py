"""
Example usage scenarios for the Travel Planner DeepAgent.

This file contains various example scenarios demonstrating
different use cases of the travel planning system.
"""

from dotenv import load_dotenv
from src.travel_planner import create_travel_planner


def example_1_quick_flight_search():
    """Example 1: Quick flight search."""
    print("\n" + "=" * 80)
    print("EXAMPLE 1: Quick Flight Search")
    print("=" * 80 + "\n")

    load_dotenv()
    planner = create_travel_planner(provider="anthropic")

    query = """
    I need to fly from Istanbul to London on December 20th.
    I'll be returning on December 27th.
    I'm traveling alone in economy class.
    What are my options?
    """

    result = planner.invoke(query)
    print("Query:", query)
    print("\nAgent response processed successfully!")


def example_2_complete_trip_planning():
    """Example 2: Complete trip planning with multiple components."""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Complete Trip Planning")
    print("=" * 80 + "\n")

    load_dotenv()
    planner = create_travel_planner(provider="anthropic")

    query = """
    I'm planning a 5-day trip to Paris in March for 2 people.

    Please help me with:
    1. Flights from New York departing March 15, returning March 20
    2. A nice 4-star hotel in the city center
    3. What will the weather be like?
    4. Recommend 3-4 must-see attractions
    5. Some good restaurants for dinner

    My budget is around $3000 for everything.
    """

    result = planner.invoke(query)
    print("Query:", query)
    print("\nAgent response processed successfully!")


def example_3_ancillary_services():
    """Example 3: Adding extra services to a booking."""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Ancillary Services")
    print("=" * 80 + "\n")

    load_dotenv()
    planner = create_travel_planner(provider="anthropic")

    query = """
    I've booked a flight (FL1234) to London for 2 passengers.

    Can you help me with:
    1. Extra baggage options - we need 2 additional checked bags
    2. Seat selection - I'd like seats with extra legroom
    3. Travel insurance options for our $2500 trip
    4. Car rental options in London for 7 days
    """

    result = planner.invoke(query)
    print("Query:", query)
    print("\nAgent response processed successfully!")


def example_4_weather_focused():
    """Example 4: Weather-focused planning."""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Weather-Focused Planning")
    print("=" * 80 + "\n")

    load_dotenv()
    planner = create_travel_planner(provider="anthropic")

    query = """
    I'm thinking of visiting Istanbul in late December.

    Can you tell me:
    1. What will the weather be like from December 20-27?
    2. What should I pack?
    3. Are there any weather concerns I should know about?
    4. What's the best time of year to visit Istanbul weather-wise?
    """

    result = planner.invoke(query)
    print("Query:", query)
    print("\nAgent response processed successfully!")


def example_5_activities_and_dining():
    """Example 5: Focus on activities and dining."""
    print("\n" + "=" * 80)
    print("EXAMPLE 5: Activities and Dining")
    print("=" * 80 + "\n")

    load_dotenv()
    planner = create_travel_planner(provider="anthropic")

    query = """
    I'll be in Istanbul for 4 days. I'm interested in:

    - Historical and cultural sites
    - Traditional Turkish cuisine experiences
    - A Bosphorus cruise if available
    - Maybe a cooking class

    Budget for activities: around $400

    What do you recommend?
    """

    result = planner.invoke(query)
    print("Query:", query)
    print("\nAgent response processed successfully!")


def example_6_budget_travel():
    """Example 6: Budget-conscious travel planning."""
    print("\n" + "=" * 80)
    print("EXAMPLE 6: Budget Travel Planning")
    print("=" * 80 + "\n")

    load_dotenv()
    planner = create_travel_planner(provider="anthropic")

    query = """
    I'm a student planning a budget trip to London for a week.

    Requirements:
    - Cheapest flight from Istanbul (I only have carry-on)
    - Budget hotel or hostel (clean and safe, under $50/night)
    - Free or low-cost activities
    - Affordable restaurant recommendations

    Total budget: $800 including flights

    Is this doable?
    """

    result = planner.invoke(query)
    print("Query:", query)
    print("\nAgent response processed successfully!")


def example_7_luxury_travel():
    """Example 7: Luxury travel planning."""
    print("\n" + "=" * 80)
    print("EXAMPLE 7: Luxury Travel Planning")
    print("=" * 80 + "\n")

    load_dotenv()
    planner = create_travel_planner(provider="anthropic")

    query = """
    Planning an anniversary trip to Paris for 4 nights.

    Looking for:
    - Business class flights from New York
    - 5-star luxury hotel with great reviews
    - Fine dining restaurant recommendations
    - Premium experiences (private tours, exclusive access)
    - Travel insurance with premium coverage

    Budget is flexible, prioritize quality and experience.
    """

    result = planner.invoke(query)
    print("Query:", query)
    print("\nAgent response processed successfully!")


def example_8_multi_city():
    """Example 8: Multi-city trip planning."""
    print("\n" + "=" * 80)
    print("EXAMPLE 8: Multi-City Trip")
    print("=" * 80 + "\n")

    load_dotenv()
    planner = create_travel_planner(provider="anthropic")

    query = """
    Planning a 2-week European trip visiting:
    1. London (4 days)
    2. Paris (5 days)
    3. Rome (5 days)

    Starting from New York on June 1st.

    Need help with:
    - Flights between cities
    - Hotels in each city (3-4 star range)
    - Weather forecast for early June
    - Must-see attractions in each city
    """

    result = planner.invoke(query)
    print("Query:", query)
    print("\nAgent response processed successfully!")


def run_all_examples():
    """Run all example scenarios."""
    examples = [
        example_1_quick_flight_search,
        example_2_complete_trip_planning,
        example_3_ancillary_services,
        example_4_weather_focused,
        example_5_activities_and_dining,
        example_6_budget_travel,
        example_7_luxury_travel,
        example_8_multi_city,
    ]

    print("\n" + "=" * 80)
    print("RUNNING ALL EXAMPLE SCENARIOS")
    print("=" * 80)

    for i, example in enumerate(examples, 1):
        print(f"\n\nRunning example {i}/{len(examples)}...")
        try:
            example()
            print(f"✅ Example {i} completed successfully")
        except Exception as e:
            print(f"❌ Example {i} failed: {str(e)}")

    print("\n" + "=" * 80)
    print("ALL EXAMPLES COMPLETED")
    print("=" * 80 + "\n")


if __name__ == "__main__":
    import sys

    if len(sys.argv) > 1:
        example_num = sys.argv[1]
        examples_map = {
            "1": example_1_quick_flight_search,
            "2": example_2_complete_trip_planning,
            "3": example_3_ancillary_services,
            "4": example_4_weather_focused,
            "5": example_5_activities_and_dining,
            "6": example_6_budget_travel,
            "7": example_7_luxury_travel,
            "8": example_8_multi_city,
            "all": run_all_examples,
        }

        example_fn = examples_map.get(example_num)
        if example_fn:
            example_fn()
        else:
            print(f"Unknown example: {example_num}")
            print("Available examples: 1-8, or 'all'")
    else:
        print("Usage: python examples.py [1-8|all]")
        print("\nAvailable examples:")
        print("  1 - Quick Flight Search")
        print("  2 - Complete Trip Planning")
        print("  3 - Ancillary Services")
        print("  4 - Weather-Focused Planning")
        print("  5 - Activities and Dining")
        print("  6 - Budget Travel")
        print("  7 - Luxury Travel")
        print("  8 - Multi-City Trip")
        print("  all - Run all examples")

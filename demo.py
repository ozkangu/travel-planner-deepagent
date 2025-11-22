"""Demo script for Travel Planner DeepAgent."""

import os
from dotenv import load_dotenv
from src.travel_planner import create_travel_planner


def simple_demo():
    """Run a simple demo of the travel planner."""

    print("=" * 80)
    print("TRAVEL PLANNER DEEPAGENT - SIMPLE DEMO")
    print("=" * 80)
    print()

    # Load environment variables
    load_dotenv()

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("⚠️  ERROR: No API key found!")
        print("Please set ANTHROPIC_API_KEY or OPENAI_API_KEY in your .env file")
        print()
        print("Example .env file:")
        print("ANTHROPIC_API_KEY=your_key_here")
        return

    # Create the travel planner
    print("🚀 Initializing Travel Planner Agent...")
    provider = "anthropic" if os.getenv("ANTHROPIC_API_KEY") else "openai"
    planner = create_travel_planner(provider=provider)
    print(f"✅ Agent initialized with {provider} provider")
    print()

    # Example queries
    example_queries = [
        "I want to travel from Istanbul to London on December 20th and return on December 27th. Can you help me find flights?",
        "What's the weather going to be like in London in late December?",
        "Can you recommend some activities to do in London?",
    ]

    for i, query in enumerate(example_queries, 1):
        print(f"\n{'=' * 80}")
        print(f"Example Query {i}:")
        print(f"{'=' * 80}")
        print(f"👤 User: {query}")
        print()
        print("🤖 Agent: Processing your request...")
        print("-" * 80)

        try:
            result = planner.invoke(query)

            # Display the conversation
            for msg in result["messages"]:
                if hasattr(msg, 'content'):
                    role = "👤 User" if msg.type == "human" else "🤖 Agent"
                    # Skip system messages and tool calls
                    if msg.type in ["human", "ai"] and not hasattr(msg, 'tool_calls'):
                        print(f"{role}: {msg.content}")
                        print()

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print()

        print("-" * 80)

    print("\n" + "=" * 80)
    print("Demo completed!")
    print("=" * 80)


def interactive_demo():
    """Run an interactive demo of the travel planner."""

    print("=" * 80)
    print("TRAVEL PLANNER DEEPAGENT - INTERACTIVE DEMO")
    print("=" * 80)
    print()

    # Load environment variables
    load_dotenv()

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("⚠️  ERROR: No API key found!")
        print("Please set ANTHROPIC_API_KEY or OPENAI_API_KEY in your .env file")
        return

    # Create the travel planner
    print("🚀 Initializing Travel Planner Agent...")
    provider = "anthropic" if os.getenv("ANTHROPIC_API_KEY") else "openai"
    planner = create_travel_planner(provider=provider)
    print(f"✅ Agent initialized with {provider} provider")
    print()

    print("💡 Tips:")
    print("  - Ask about flights, hotels, activities, weather, etc.")
    print("  - Type 'exit' or 'quit' to end the conversation")
    print("  - Type 'help' for example queries")
    print()

    # Conversation loop
    conversation_history = []

    while True:
        print("-" * 80)
        user_input = input("👤 You: ").strip()
        print()

        if not user_input:
            continue

        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("👋 Thanks for using Travel Planner! Have a great trip!")
            break

        if user_input.lower() == 'help':
            print("📋 Example queries:")
            print("  - Find me flights from New York to Paris on March 15th")
            print("  - What hotels are available in Paris for March 15-20?")
            print("  - What's the weather like in Paris in March?")
            print("  - Recommend some activities in Paris")
            print("  - I need travel insurance for a $2000 trip")
            print("  - What baggage options are available for my flight?")
            print()
            continue

        try:
            print("🤖 Agent: Processing your request...")
            print()

            result = planner.invoke(user_input)

            # Get the latest agent response
            for msg in reversed(result["messages"]):
                if msg.type == "ai" and not hasattr(msg, 'tool_calls'):
                    print(f"🤖 Agent: {msg.content}")
                    print()
                    break

            conversation_history.append({"user": user_input, "agent": result})

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print()


def mock_tools_demo():
    """Demonstrate the mock tools directly."""

    print("=" * 80)
    print("MOCK TOOLS DEMONSTRATION")
    print("=" * 80)
    print()

    from src.tools import (
        search_flights,
        search_hotels,
        get_baggage_options,
        search_activities,
        get_weather_forecast,
        get_insurance_options
    )

    # Flight search demo
    print("1️⃣  FLIGHT SEARCH")
    print("-" * 80)
    flights = search_flights.invoke({
        "origin": "Istanbul",
        "destination": "London",
        "departure_date": "2024-12-20",
        "return_date": "2024-12-27",
        "passengers": 2,
        "cabin_class": "economy"
    })
    print(f"Found {len(flights)} flights:")
    for flight in flights[:2]:  # Show first 2
        print(f"  ✈️  {flight['airline']['name']} - ${flight['total_price']} for {flight.get('passengers', 2)} passengers")
        print(f"      Departure: {flight['departure_date']} at {flight['departure_time']}")
        print(f"      Duration: {flight['duration']}, Stops: {flight['stops']}")
    print()

    # Hotel search demo
    print("2️⃣  HOTEL SEARCH")
    print("-" * 80)
    hotels = search_hotels.invoke({
        "city": "London",
        "check_in": "2024-12-20",
        "check_out": "2024-12-27",
        "guests": 2,
        "min_stars": 4
    })
    print(f"Found {len(hotels)} hotels:")
    for hotel in hotels[:2]:  # Show first 2
        print(f"  🏨 {hotel['name']} - {hotel['stars']}⭐ (Rating: {hotel['rating']}/10)")
        print(f"      ${hotel['price_per_night']}/night - Total: ${hotel['total_price']}")
        print(f"      Location: {hotel['location']['neighborhood']}")
    print()

    # Activity search demo
    print("3️⃣  ACTIVITY SEARCH")
    print("-" * 80)
    activities = search_activities.invoke({
        "city": "Istanbul",
        "category": "all",
        "max_price": 100
    })
    print(f"Found {len(activities)} activities:")
    for activity in activities[:3]:  # Show first 3
        print(f"  🎯 {activity['name']} - ${activity['price']}")
        print(f"      Category: {activity['category']}, Duration: {activity['duration_hours']}h")
        print(f"      Rating: {activity['rating']}/5 ({activity['reviews']} reviews)")
    print()

    # Weather forecast demo
    print("4️⃣  WEATHER FORECAST")
    print("-" * 80)
    weather = get_weather_forecast.invoke({
        "city": "London",
        "date": "2024-12-20",
        "days": 7
    })
    print(f"Weather in {weather['city']}:")
    print(f"  {weather['summary']}")
    print(f"  Travel advice:")
    for advice in weather['travel_advice']:
        print(f"    - {advice}")
    print()

    # Insurance options demo
    print("5️⃣  TRAVEL INSURANCE OPTIONS")
    print("-" * 80)
    insurance = get_insurance_options.invoke({
        "trip_type": "international",
        "total_trip_cost": 2000,
        "passengers": 2,
        "destination_country": "GB"
    })
    print(f"Found {len(insurance)} insurance plans:")
    for plan in insurance:
        print(f"  🛡️  {plan['name']} - ${plan['total_price']} total")
        print(f"      Medical coverage: ${plan['coverage']['medical_emergency']['max_amount']}")
        print(f"      Trip cancellation: ${plan['coverage']['trip_cancellation']['max_amount']}")
    print()

    # Baggage options demo
    print("6️⃣  BAGGAGE OPTIONS")
    print("-" * 80)
    baggage = get_baggage_options.invoke({
        "flight_id": "FL1234",
        "passengers": 2
    })
    print(f"Included baggage:")
    print(f"  Cabin: {baggage['included_baggage']['cabin']['weight']}")
    print(f"  Checked: {baggage['included_baggage']['checked']['weight']}")
    print(f"\nAdditional options:")
    for option in baggage['additional_options'][:3]:
        print(f"  💼 {option['description']} - ${option['price_per_bag']}/bag")
    print()

    print("=" * 80)
    print("Mock tools demonstration completed!")
    print("=" * 80)


if __name__ == "__main__":
    import sys

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                    TRAVEL PLANNER DEEPAGENT DEMO                             ║
║                                                                              ║
║  A demonstration of LangGraph DeepAgent framework for travel planning       ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        print("Select demo mode:")
        print("  1. Simple Demo (pre-defined queries)")
        print("  2. Interactive Demo (chat with the agent)")
        print("  3. Mock Tools Demo (test tools directly)")
        print()
        choice = input("Enter your choice (1-3): ").strip()

        mode_map = {
            "1": "simple",
            "2": "interactive",
            "3": "tools"
        }
        mode = mode_map.get(choice, "simple")

    print()

    if mode == "interactive":
        interactive_demo()
    elif mode == "tools":
        mock_tools_demo()
    else:
        simple_demo()

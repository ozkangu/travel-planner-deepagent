"""
Real scenario demo with mock LLM responses.

Scenario: Plan a 5-day trip to Paris from Istanbul
Dates: 2024-12-20 to 2024-12-25
Passengers: 2 people
Budget: $3000
"""

import asyncio
from unittest.mock import AsyncMock, Mock
import json
from datetime import datetime

# Mock the LLM before importing
from unittest.mock import patch


async def demo_paris_trip():
    """Demo: Istanbul to Paris trip planning."""

    print("\n" + "="*80)
    print("🌍 TRAVEL PLANNER V2 - REAL SCENARIO DEMO")
    print("="*80)

    print("\n📝 User Request:")
    print("   'Plan a 5-day trip to Paris from Istanbul")
    print("   December 20-25, 2024")
    print("   2 people, budget $3000'")

    # Mock LLM responses
    intent_response = {
        "intent": "plan_trip",
        "origin": "Istanbul",
        "destination": "Paris",
        "departure_date": "2024-12-20",
        "return_date": "2024-12-25",
        "num_passengers": 2,
        "budget": 3000.0,
        "requires_flights": True,
        "requires_hotels": True,
        "requires_activities": True,
        "requires_weather": True,
        "preferences": {
            "cabin_class": "economy",
            "hotel_rating": 4,
            "activities": ["museums", "restaurants", "sightseeing"]
        }
    }

    itinerary_response = """# 5-Day Paris Itinerary (December 20-25, 2024)

## Trip Overview
- **Travelers**: 2 people
- **Budget**: $3,000
- **Dates**: December 20-25, 2024

## Flight Details
**Outbound Flight**: Istanbul (IST) → Paris (CDG)
- **Airline**: Turkish Airlines
- **Departure**: December 20, 2024 at 10:30 AM
- **Arrival**: December 20, 2024 at 2:15 PM (local)
- **Duration**: 3h 45m (direct flight)
- **Price**: $450 per person × 2 = **$900**

**Return Flight**: Paris (CDG) → Istanbul (IST)
- **Airline**: Turkish Airlines
- **Departure**: December 25, 2024 at 4:00 PM
- **Arrival**: December 25, 2024 at 9:30 PM (local)
- **Duration**: 3h 30m (direct flight)
- **Price**: Included in round-trip

## Accommodation
**Hotel**: Le Marais Boutique Hotel ⭐⭐⭐⭐
- **Location**: Le Marais district (central Paris)
- **Check-in**: December 20, 2024
- **Check-out**: December 25, 2024
- **Nights**: 5 nights
- **Price**: $180/night × 5 = **$900**
- **Amenities**: Free WiFi, breakfast included, central location
- **Distance to center**: 0.5 km

## Daily Itinerary

### Day 1 (December 20) - Arrival
- **Morning**: Arrive at CDG at 2:15 PM
- **Afternoon**: Check into hotel, explore Le Marais neighborhood
- **Evening**: Dinner at L'As du Fallafel (famous falafel, ~$20)
- **Weather**: 45°F, partly cloudy, 30% rain chance

### Day 2 (December 21) - Historic Paris
- **Morning**: Visit Louvre Museum (€17 per person)
- **Afternoon**: Walk through Tuileries Garden, Place de la Concorde
- **Evening**: Seine River cruise (€15 per person)
- **Dinner**: Traditional bistro in Saint-Germain (~$60)
- **Weather**: 43°F, overcast, 40% rain chance

### Day 3 (December 22) - Eiffel Tower & Montmartre
- **Morning**: Eiffel Tower visit with summit access (€28 per person)
- **Afternoon**: Climb to Sacré-Cœur Basilica in Montmartre
- **Evening**: Explore Montmartre artists' square
- **Dinner**: French cuisine at Le Moulin de la Galette (~$70)
- **Weather**: 41°F, light rain possible, 50% rain chance

### Day 4 (December 23) - Versailles Day Trip
- **Full Day**: Palace of Versailles (€20 per person + train €7)
- **Highlights**: Hall of Mirrors, gardens, Marie Antoinette's estate
- **Evening**: Return to Paris, dinner in Latin Quarter (~$50)
- **Weather**: 44°F, cloudy, 20% rain chance

### Day 5 (December 24) - Christmas Eve in Paris
- **Morning**: Notre-Dame exterior, Sainte-Chapelle (€11 per person)
- **Afternoon**: Shopping on Champs-Élysées, Arc de Triomphe
- **Evening**: Christmas Eve dinner at traditional brasserie (~$100)
- **Weather**: 46°F, clear, festive atmosphere

### Day 6 (December 25) - Departure
- **Morning**: Last-minute shopping, breakfast
- **Afternoon**: Depart for airport at 1:00 PM
- **Flight**: 4:00 PM departure

## Weather Summary
- **Temperature Range**: 41-46°F (5-8°C)
- **Conditions**: Cool, mostly cloudy with occasional rain
- **Packing Recommendations**:
  - Warm layers (sweaters, jackets)
  - Waterproof coat or umbrella
  - Comfortable walking shoes (waterproof)
  - Scarf and gloves for evening walks

## Activities & Attractions Included
1. **Louvre Museum** - World's largest art museum (€17/person)
2. **Eiffel Tower Summit** - Iconic landmark visit (€28/person)
3. **Seine River Cruise** - Evening boat tour (€15/person)
4. **Versailles Palace** - Day trip to royal palace (€20/person)
5. **Sainte-Chapelle** - Gothic chapel with stained glass (€11/person)

## Budget Breakdown
| Category | Cost |
|----------|------|
| Flights (round-trip, 2 people) | $900 |
| Hotel (5 nights) | $900 |
| Activities & Attractions | $274 |
| Meals (estimate) | $600 |
| Transportation (metro, train) | $100 |
| **Total** | **$2,774** |
| **Remaining Budget** | **$226** |

## 💡 Recommendations
1. ✅ **You're within budget!** $226 remaining for souvenirs and extras
2. 🎄 **Christmas Atmosphere**: Paris is beautiful during Christmas with decorations and markets
3. 🌧️ **Weather Prep**: Pack warm, waterproof clothing - December can be rainy
4. 🚇 **Get a Paris Visite Pass**: Unlimited metro for €38.35 (5 days) - saves money
5. 🍷 **Wine & Cheese**: Budget $50 for a wine tasting experience
6. 🎨 **Book Museums Early**: Louvre gets crowded - book tickets online in advance
7. 🌙 **Evening Strolls**: Paris lights are magical at night, especially Champs-Élysées

## Important Tips
- 📱 Download Google Maps offline for Paris
- 💳 Credit cards widely accepted, but carry some euros
- 🗣️ Learn basic French phrases (Bonjour, Merci, S'il vous plaît)
- ⏰ Most shops close on December 25 (Christmas Day) - plan accordingly
- 🎫 Consider Paris Museum Pass (€62) for unlimited museum access

**Bon voyage! Have an amazing trip to Paris!** 🇫🇷✨
"""

    # Step 1: Intent Classification
    print("\n" + "="*80)
    print("STEP 1: Intent Classification")
    print("="*80)

    print("\n🤖 Analyzing user query with LLM...")
    await asyncio.sleep(0.5)  # Simulate LLM call

    print(f"\n✅ Intent Classification Results:")
    print(f"   Intent: {intent_response['intent']}")
    print(f"   Origin: {intent_response['origin']}")
    print(f"   Destination: {intent_response['destination']}")
    print(f"   Dates: {intent_response['departure_date']} to {intent_response['return_date']}")
    print(f"   Passengers: {intent_response['num_passengers']}")
    print(f"   Budget: ${intent_response['budget']}")
    print(f"   Preferences: {intent_response['preferences']}")

    # Step 2: Routing
    print("\n" + "="*80)
    print("STEP 2: Workflow Routing")
    print("="*80)

    print("\n🔀 Conditional router determining required services...")
    print(f"   ✅ Flights: {intent_response['requires_flights']}")
    print(f"   ✅ Hotels: {intent_response['requires_hotels']}")
    print(f"   ✅ Weather: {intent_response['requires_weather']}")
    print(f"   ✅ Activities: {intent_response['requires_activities']}")

    # Step 3: Parallel Searches
    print("\n" + "="*80)
    print("STEP 3: Parallel Service Calls")
    print("="*80)

    print("\n⚡ Running searches in parallel (no LLM needed)...")

    # Simulate parallel execution
    tasks = ["Searching flights", "Searching hotels", "Checking weather", "Finding activities"]
    for i, task in enumerate(tasks, 1):
        await asyncio.sleep(0.3)
        print(f"   [{i}/4] {task}... ✅ Done")

    # Mock results
    print("\n📊 Search Results:")
    print("\n   ✈️  FLIGHTS (5 options found):")
    print("      Option 1: Turkish Airlines IST→CDG")
    print("         • Departure: Dec 20, 10:30 AM")
    print("         • Arrival: Dec 20, 2:15 PM")
    print("         • Duration: 3h 45m (direct)")
    print("         • Price: $450/person")
    print("         • Rating: ⭐⭐⭐⭐⭐")

    print("\n   🏨 HOTELS (8 options found):")
    print("      Option 1: Le Marais Boutique Hotel ⭐⭐⭐⭐")
    print("         • Location: Le Marais (0.5km to center)")
    print("         • Rating: 4.3/5")
    print("         • Price: $180/night")
    print("         • Total (5 nights): $900")
    print("         • Amenities: WiFi, Breakfast, Central location")

    print("\n   🌤️  WEATHER (5-day forecast):")
    print("      Dec 20: Partly cloudy, 45°F, 30% rain")
    print("      Dec 21: Overcast, 43°F, 40% rain")
    print("      Dec 22: Light rain, 41°F, 50% rain")
    print("      Dec 23: Cloudy, 44°F, 20% rain")
    print("      Dec 24: Clear, 46°F, Christmas atmosphere!")

    print("\n   🎭 ACTIVITIES (12 options found):")
    print("      1. Louvre Museum - €17/person, 3-4 hours, ⭐⭐⭐⭐⭐")
    print("      2. Eiffel Tower Summit - €28/person, 2 hours, ⭐⭐⭐⭐⭐")
    print("      3. Seine River Cruise - €15/person, 1 hour, ⭐⭐⭐⭐")
    print("      4. Versailles Palace - €20/person, full day, ⭐⭐⭐⭐⭐")
    print("      5. Sainte-Chapelle - €11/person, 1 hour, ⭐⭐⭐⭐⭐")

    # Step 4: Itinerary Generation
    print("\n" + "="*80)
    print("STEP 4: Itinerary Generation")
    print("="*80)

    print("\n🤖 Generating comprehensive itinerary with LLM...")
    await asyncio.sleep(0.5)  # Simulate LLM call

    print("\n✅ Itinerary Generated!")
    print("\n" + "="*80)
    print(itinerary_response)
    print("="*80)

    # Summary
    print("\n" + "="*80)
    print("📊 WORKFLOW SUMMARY")
    print("="*80)

    print("\n✅ Workflow Completed Successfully!")
    print("\n📈 Performance Metrics:")
    print("   • Total time: ~4 seconds")
    print("   • LLM calls: 2 (Intent + Itinerary)")
    print("   • Service calls: 4 (Flight, Hotel, Weather, Activities)")
    print("   • Total cost estimate: ~$0.021")

    print("\n💰 Budget Analysis:")
    print("   • Total Budget: $3,000")
    print("   • Estimated Cost: $2,774")
    print("   • Remaining: $226 (7.5%)")
    print("   • Status: ✅ Within Budget!")

    print("\n🎯 Trip Highlights:")
    print("   • Direct flights with Turkish Airlines")
    print("   • 4-star hotel in central Paris (Le Marais)")
    print("   • 5 major attractions included")
    print("   • Christmas atmosphere in Paris!")
    print("   • Cool weather (41-46°F) - pack warm clothes")

    print("\n📝 Completed Steps:")
    print("   1. ✅ Intent Classification")
    print("   2. ✅ Conditional Routing")
    print("   3. ✅ Parallel Service Calls (Flights, Hotels, Weather, Activities)")
    print("   4. ✅ Itinerary Generation")

    print("\n" + "="*80)
    print("🎉 SUCCESS! Your Paris trip is planned and ready to book!")
    print("="*80 + "\n")


async def demo_architecture_visualization():
    """Show how the workflow actually runs."""

    print("\n" + "="*80)
    print("🔍 WORKFLOW ARCHITECTURE VISUALIZATION")
    print("="*80)

    print("""
User Query: "Plan 5-day trip to Paris from Istanbul, Dec 20-25, 2 people, $3000"
    ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Intent Classifier Node (LLM)                        │
│ ────────────────────────────────────────────────────────    │
│ Input: Natural language query                                │
│ Output: Structured parameters + routing flags                │
│ Time: ~2 seconds                                             │
│ Cost: ~$0.01                                                 │
└─────────────────────────────────────────────────────────────┘
    ↓
{
  "intent": "plan_trip",
  "origin": "Istanbul",
  "destination": "Paris",
  "departure_date": "2024-12-20",
  "return_date": "2024-12-25",
  "num_passengers": 2,
  "budget": 3000,
  "requires_flights": true,   ← Routing flags
  "requires_hotels": true,    ← set by LLM
  "requires_activities": true,
  "requires_weather": true
}
    ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Conditional Router (Code, not LLM!)                 │
│ ────────────────────────────────────────────────────────    │
│ Checks routing flags and decides which nodes to run         │
│ Time: <1 millisecond                                         │
│ Cost: $0 (pure code logic)                                  │
└─────────────────────────────────────────────────────────────┘
    ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Parallel Service Nodes (No LLM!)                    │
│ ─────────────────────────────────────────────────────────   │
│ These run in parallel because they're independent:          │
│                                                              │
│  ┌───────────┐  ┌───────────┐  ┌───────────┐  ┌─────────┐ │
│  │  Flight   │  │   Hotel   │  │  Weather  │  │Activity │ │
│  │  Search   │  │  Search   │  │   Check   │  │ Search  │ │
│  └─────┬─────┘  └─────┬─────┘  └─────┬─────┘  └────┬────┘ │
│        │              │              │             │       │
│        └──────────────┴──────────────┴─────────────┘       │
│                                                             │
│ Time: ~1-2 seconds (parallel execution)                     │
│ Cost: $0 (just API calls to search services)               │
└─────────────────────────────────────────────────────────────┘
    ↓
{
  "flight_options": [5 flights],
  "hotel_options": [8 hotels],
  "weather_forecast": [5 days],
  "activity_options": [12 activities]
}
    ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Itinerary Generator Node (LLM)                      │
│ ────────────────────────────────────────────────────────    │
│ Input: All search results + user preferences                │
│ Output: Beautiful, comprehensive itinerary                  │
│ Time: ~2 seconds                                             │
│ Cost: ~$0.011                                                │
└─────────────────────────────────────────────────────────────┘
    ↓
📄 Final Itinerary (Markdown)

════════════════════════════════════════════════════════════
TOTAL WORKFLOW:
  • Steps: 4 (1 → 2 → 3 → 4)
  • Time: ~4-6 seconds
  • LLM Calls: 2 (Step 1 + Step 4)
  • Cost: ~$0.021
════════════════════════════════════════════════════════════

🎯 KEY ADVANTAGES:
  ✅ Only 2 LLM calls (not 12 like V1!)
  ✅ Steps 2-3 are pure code (fast & free)
  ✅ Parallel execution possible in Step 3
  ✅ Deterministic routing (no LLM guessing)
  ✅ Easy to debug (can inspect state at each step)
""")


async def main():
    """Run all demos."""
    await demo_paris_trip()
    await demo_architecture_visualization()


if __name__ == "__main__":
    asyncio.run(main())

# Travel Planner V2 - Quick Start Guide

## 🚀 Quick Start (2 minutes)

### Installation

```bash
# Install dependencies
uv sync

# Set API key
export ANTHROPIC_API_KEY="your-key-here"
```

### Basic Usage

```python
import asyncio
from src_v2 import TravelPlannerV2

async def main():
    # Create planner
    planner = TravelPlannerV2(provider="anthropic", verbose=True)

    # Plan a trip
    result = await planner.plan_trip(
        "Plan a 5-day trip to Tokyo in March for 2 people, budget $5000"
    )

    # Print results
    print(result["itinerary"])
    print(f"Total cost: ${result['total_cost']:.2f}")

asyncio.run(main())
```

**That's it!** ✨

---

## 📚 Common Use Cases

### 1. Search Flights Only

```python
result = await planner.search_flights(
    origin="New York",
    destination="London",
    departure_date="2024-06-15",
    return_date="2024-06-22",
    num_passengers=2,
    budget=2000.0
)

# Access flight options
for flight in result["flight_options"]:
    print(f"{flight['airline']}: ${flight['price']}")
```

### 2. Search Hotels Only

```python
result = await planner.search_hotels(
    destination="Paris",
    check_in="2024-07-01",
    check_out="2024-07-07",
    num_guests=2,
    min_rating=4.0,
    budget=1500.0
)

# Access hotel options
for hotel in result["hotel_options"]:
    print(f"{hotel['name']}: ${hotel['price_per_night']}/night")
```

### 3. Full Trip with Preferences

```python
result = await planner.plan_trip(
    query="Plan a beach vacation in Hawaii",
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
        "activities": ["snorkeling", "hiking"]
    }
)
```

### 4. Quick One-Liner

```python
from src_v2 import plan_trip

result = await plan_trip("Weekend trip to Barcelona")
```

---

## 🎯 What You Get Back

The result is a `TravelPlannerState` dictionary with:

```python
{
    # Trip details
    "origin": "New York",
    "destination": "Tokyo",
    "departure_date": "2024-03-15",
    "return_date": "2024-03-20",

    # Search results
    "flight_options": [...],      # List of flights
    "hotel_options": [...],        # List of hotels
    "activity_options": [...],     # List of activities
    "weather_forecast": [...],     # Daily weather

    # Final output
    "itinerary": "...",           # Full itinerary text
    "total_cost": 4250.50,        # Total price
    "recommendations": [...],      # Tips and suggestions

    # Workflow info
    "completed_steps": [...],     # What ran
    "errors": [...]               # Any issues
}
```

---

## 🛠️ Advanced Usage

### Use Different LLM Providers

```python
# Anthropic (default)
planner = TravelPlannerV2(provider="anthropic")

# OpenAI
planner = TravelPlannerV2(provider="openai")

# OpenRouter
planner = TravelPlannerV2(
    provider="openrouter",
    model="anthropic/claude-3.5-sonnet"
)
```

### Enable Verbose Logging

```python
planner = TravelPlannerV2(verbose=True)
# Prints workflow progress as it runs
```

### Access Individual Results

```python
result = await planner.plan_trip("Trip to Paris")

# Flights
print(f"Found {len(result['flight_options'])} flights")
for flight in result["flight_options"]:
    print(f"  {flight['airline']}: {flight['departure_time']} → {flight['arrival_time']}")

# Hotels
print(f"Found {len(result['hotel_options'])} hotels")
for hotel in result["hotel_options"]:
    print(f"  {hotel['name']}: {hotel['rating']}★ - ${hotel['price_per_night']}/night")

# Weather
for day in result["weather_forecast"]:
    print(f"  {day['date']}: {day['condition']}, {day['temperature_high']}°F")

# Activities
for activity in result["activity_options"]:
    print(f"  {activity['name']}: {activity['type']} - ${activity['price']}")
```

---

## 🐛 Troubleshooting

### No API Key Error

```python
# Set in terminal
export ANTHROPIC_API_KEY="sk-ant-..."

# Or in Python
import os
os.environ["ANTHROPIC_API_KEY"] = "sk-ant-..."
```

### Missing Dependencies

```bash
# Using uv (recommended)
uv sync

# Or pip
pip install langgraph langchain langchain-anthropic
```

### Import Errors

```python
# Make sure you're using src_v2, not src
from src_v2 import TravelPlannerV2  # ✅ Correct
from src import create_travel_planner  # ❌ Old V1
```

### Async Errors

```python
# Always use asyncio.run() or await
import asyncio

# ✅ Correct
asyncio.run(planner.plan_trip("..."))

# ❌ Wrong
planner.plan_trip("...")  # Missing await
```

---

## 📊 Understanding the Workflow

The system runs in this order:

1. **Intent Classification** (LLM)
   - Analyzes your query
   - Extracts: origin, destination, dates, budget, preferences
   - Decides what services to run

2. **Parallel Searches** (Fast, no LLM)
   - Flight search (if needed)
   - Hotel search (if needed)
   - Weather check (if needed)
   - Activity search (if needed)

3. **Itinerary Generation** (LLM)
   - Combines all results
   - Creates day-by-day plan
   - Adds recommendations

**Total time**: ~4-6 seconds
**LLM calls**: Only 2 (intent + itinerary)

---

## 💡 Pro Tips

### 1. Be Specific

```python
# ❌ Vague
"I want to go somewhere"

# ✅ Specific
"Plan a 5-day trip to Tokyo in March for 2 people, budget $5000"
```

### 2. Use Preferences

```python
preferences={
    "cabin_class": "business",     # economy, premium_economy, business, first
    "hotel_rating": 4.5,           # 1-5 stars
    "hotel_amenities": ["pool", "gym", "spa"],
    "activities": ["museums", "food tours", "hiking"],
    "activity_types": ["cultural", "adventure", "relaxation"]
}
```

### 3. Check Errors

```python
result = await planner.plan_trip("...")

if result["errors"]:
    print("Issues encountered:")
    for error in result["errors"]:
        print(f"  - {error}")
```

### 4. Reuse Planner Instance

```python
# ✅ Efficient (reuse)
planner = TravelPlannerV2()
result1 = await planner.plan_trip("Trip to Tokyo")
result2 = await planner.plan_trip("Trip to Paris")

# ❌ Wasteful (recreate every time)
result1 = await TravelPlannerV2().plan_trip("Trip to Tokyo")
result2 = await TravelPlannerV2().plan_trip("Trip to Paris")
```

---

## 🧪 Testing

Run the quick tests:

```bash
python test_v2_quick.py
```

Run the examples:

```bash
python examples_v2.py
```

---

## 📖 More Resources

- **Full Documentation**: See `src_v2/README.md`
- **Architecture Details**: See `V1_VS_V2_COMPARISON.md`
- **Examples**: See `examples_v2.py`
- **Source Code**: Browse `src_v2/` directory

---

## 🤝 Need Help?

Common questions:

**Q: Can I use GPT-4 instead of Claude?**
A: Yes! Use `provider="openai"`

**Q: How do I get just flights without hotels?**
A: Use `planner.search_flights()` or set a query like "Find flights to London"

**Q: Is it free?**
A: No, it uses LLM APIs (Anthropic/OpenAI). Cost is ~$0.02 per full trip plan.

**Q: Can I run it locally?**
A: The code runs locally, but it calls cloud LLM APIs. You need an API key.

**Q: Does it actually book flights?**
A: Not yet - this is a planning tool. Booking integration is roadmap.

---

**Ready to start?** Run this:

```python
import asyncio
from src_v2 import TravelPlannerV2

async def main():
    planner = TravelPlannerV2(verbose=True)
    result = await planner.plan_trip(
        "Plan my dream vacation!"  # Be more specific! 😄
    )
    print(result["itinerary"])

asyncio.run(main())
```

🎉 **Happy traveling!**

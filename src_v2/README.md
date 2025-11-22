# Travel Planner V2 - LangGraph Architecture

## Overview

Travel Planner V2 is a production-ready travel planning agent built with **LangGraph** for explicit DAG (Directed Acyclic Graph) workflows. This architecture provides significant improvements over the V1 agent-based approach.

## Why LangGraph? (V2 vs V1)

### V1 Problems (DeepAgent approach):
- ❌ **Opaque control flow**: Supervisor agent decides routing - non-deterministic
- ❌ **Hard to debug**: Can't easily trace decision path
- ❌ **High latency**: Every routing decision requires LLM call
- ❌ **High cost**: Unnecessary supervisor LLM invocations
- ❌ **Limited parallelism**: Agent-based delegation is sequential
- ❌ **Error handling complexity**: Retry logic hard to implement

### V2 Advantages (LangGraph approach):
- ✅ **Explicit control flow**: Graph structure is visible and deterministic
- ✅ **Easy debugging**: State transitions are traceable
- ✅ **Lower latency**: Conditional routing in code, not LLM
- ✅ **Cost efficient**: Only use LLM for actual work, not routing
- ✅ **True parallelism**: Independent nodes can run concurrently
- ✅ **Robust error handling**: Per-node error handling and retries

## Architecture

```
┌─────────────┐
│ User Query  │
└──────┬──────┘
       │
       ▼
┌──────────────────┐
│ Intent Classify  │  ◄─── LLM extracts: intent, params, requirements
└──────┬───────────┘
       │
       ▼
  ┌────┴────┐  Conditional routing based on intent
  │         │
  ▼         ▼
┌─────┐   ┌────┐
│ END │   │ Go │
└─────┘   └─┬──┘
            │
            ▼
  ┌─────────────────┐
  │ Parallel Search │ ◄─── These can run in parallel
  └────────┬────────┘
           │
    ┌──────┼──────┬──────┐
    │      │      │      │
    ▼      ▼      ▼      ▼
┌────────┐ ┌─────┐ ┌────────┐ ┌───────────┐
│Flights │ │Hotel│ │Weather │ │Activities │
└───┬────┘ └──┬──┘ └───┬────┘ └─────┬─────┘
    │         │        │            │
    └─────────┴────────┴────────────┘
                  │
                  ▼
       ┌────────────────────┐
       │ Aggregate Results  │
       └─────────┬──────────┘
                 │
         ┌───────┴────────┐
         ▼                ▼
    ┌─────────┐    ┌─────────────┐
    │   END   │    │  Generate   │ ◄─── LLM creates itinerary
    │(partial)│    │  Itinerary  │
    └─────────┘    └──────┬──────┘
                          │
                          ▼
                     ┌────────┐
                     │  END   │
                     └────────┘
```

## Directory Structure

```
src_v2/
├── __init__.py              # Main exports
├── travel_planner_v2.py     # User-facing API
├── schemas/
│   ├── __init__.py
│   └── state.py             # TravelPlannerState and data models
├── nodes/
│   ├── __init__.py
│   ├── intent_classifier.py # Intent analysis & parameter extraction
│   ├── flight_node.py       # Flight search logic
│   ├── hotel_node.py        # Hotel search logic
│   ├── weather_node.py      # Weather forecast logic
│   ├── activity_node.py     # Activity search logic
│   └── itinerary_node.py    # Result aggregation & itinerary generation
└── workflows/
    ├── __init__.py
    └── travel_workflow.py   # LangGraph workflow definition
```

## Key Components

### 1. State Management (`schemas/state.py`)

**TravelPlannerState** is a TypedDict that flows through all nodes:

```python
class TravelPlannerState(TypedDict):
    # User inputs
    user_query: str
    origin: Optional[str]
    destination: Optional[str]
    departure_date: Optional[str]
    ...

    # Intent & routing flags
    intent: Literal["plan_trip", "search_flights", ...]
    requires_flights: bool
    requires_hotels: bool
    ...

    # Search results
    flight_options: List[FlightOption]
    hotel_options: List[HotelOption]
    ...

    # Final outputs
    itinerary: Optional[str]
    total_cost: float
    recommendations: List[str]
```

### 2. Nodes (`nodes/`)

Each node is a pure function: `async def node(state, llm) -> Dict[str, Any]`

- **intent_classifier**: Analyzes query, extracts parameters, sets routing flags
- **flight_node**: Searches flights, validates params, returns options
- **hotel_node**: Searches hotels, calculates nights, filters by rating
- **weather_node**: Fetches forecast, generates packing recommendations
- **activity_node**: Searches attractions/activities, filters by interests
- **itinerary_node**: Aggregates all results, generates final itinerary with LLM

### 3. Workflow (`workflows/travel_workflow.py`)

Defines the graph structure with conditional routing:

```python
workflow = StateGraph(TravelPlannerState)

# Add nodes
workflow.add_node("classify_intent", classify_intent_node)
workflow.add_node("search_flights", search_flights_node)
...

# Conditional edges
workflow.add_conditional_edges(
    "classify_intent",
    route_after_intent,  # Returns "parallel_search" or "end"
    {
        "parallel_search": "search_flights",
        "end": END
    }
)
```

### 4. API Wrapper (`travel_planner_v2.py`)

User-friendly interface:

```python
planner = TravelPlannerV2(provider="anthropic")
result = await planner.plan_trip("Plan a trip to Tokyo")
```

## Usage Examples

### Full Trip Planning

```python
from src_v2 import TravelPlannerV2

planner = TravelPlannerV2(provider="anthropic", verbose=True)

result = await planner.plan_trip(
    query="Plan a 5-day trip to Tokyo in March for 2 people",
    budget=5000.0,
    preferences={
        "cabin_class": "economy",
        "hotel_rating": 4,
        "activities": ["museums", "restaurants"]
    }
)

print(result["itinerary"])
print(f"Total cost: ${result['total_cost']}")
```

### Flight Search Only

```python
result = await planner.search_flights(
    origin="New York",
    destination="London",
    departure_date="2024-06-15",
    return_date="2024-06-22",
    num_passengers=2
)

for flight in result["flight_options"]:
    print(f"{flight['airline']}: ${flight['price']}")
```

### Hotel Search Only

```python
result = await planner.search_hotels(
    destination="Paris",
    check_in="2024-07-01",
    check_out="2024-07-07",
    num_guests=2,
    min_rating=4.0
)
```

### Quick Planning

```python
from src_v2 import plan_trip

result = await plan_trip(
    "Weekend trip to Barcelona",
    provider="anthropic"
)
```

## Extending the System

### Adding a New Service Node

1. **Create the node function**:

```python
# src_v2/nodes/restaurant_node.py
async def search_restaurants_node(state, llm) -> Dict[str, Any]:
    destination = state.get("destination")
    # ... search logic ...
    return {
        "restaurant_options": results,
        "current_step": "restaurant_search",
        "completed_steps": state.get("completed_steps", []) + ["restaurant_search"]
    }
```

2. **Update state schema**:

```python
# src_v2/schemas/state.py
class TravelPlannerState(TypedDict, total=False):
    ...
    restaurant_options: List[RestaurantOption]
    requires_restaurants: bool
```

3. **Add to workflow**:

```python
# src_v2/workflows/travel_workflow.py
workflow.add_node("search_restaurants", search_restaurants_node)
workflow.add_edge("search_activities", "search_restaurants")
```

### Adding Conditional Logic

```python
def should_search_premium_hotels(state: TravelPlannerState) -> bool:
    return state.get("budget", 0) > 3000

workflow.add_conditional_edges(
    "search_hotels",
    lambda s: "premium" if should_search_premium_hotels(s) else "standard",
    {
        "premium": "search_luxury_hotels",
        "standard": "check_weather"
    }
)
```

## Performance Optimizations

### 1. Parallel Execution

Future enhancement: Use LangGraph's parallel execution for independent nodes:

```python
from langgraph.graph import StateGraph

# These nodes can run truly in parallel
parallel_searches = ["search_flights", "search_hotels", "check_weather"]
```

### 2. Caching

Add caching for repeated searches:

```python
from functools import lru_cache

@lru_cache(maxsize=100)
def get_cached_flights(origin, dest, date):
    return search_flights(origin, dest, date)
```

### 3. Streaming

Stream intermediate results:

```python
async for chunk in workflow.astream(initial_state):
    print(f"Step completed: {chunk['current_step']}")
```

## Error Handling

Each node handles errors gracefully:

```python
try:
    result = search_flights.invoke(params)
    return {"flight_options": result}
except Exception as e:
    return {
        "flight_options": [],
        "errors": state.get("errors", []) + [f"Flight search error: {e}"]
    }
```

Retry logic can be added at the workflow level:

```python
workflow.add_node(
    "search_flights_with_retry",
    retry_node(search_flights_node, max_retries=3)
)
```

## Testing

```python
import pytest
from src_v2.nodes.flight_node import search_flights_node

@pytest.mark.asyncio
async def test_flight_search():
    state = {
        "origin": "NYC",
        "destination": "LAX",
        "departure_date": "2024-06-15"
    }
    result = await search_flights_node(state, mock_llm)
    assert len(result["flight_options"]) > 0
```

## Monitoring

Use LangSmith for workflow observability:

```python
from langsmith import Client

planner = TravelPlannerV2(
    provider="anthropic",
    verbose=True
)
# LangSmith will automatically trace all steps
```

## Migration from V1

To migrate from V1 (DeepAgent) to V2 (LangGraph):

1. **Replace imports**:
```python
# OLD
from src.travel_planner import create_travel_planner
agent = create_travel_planner()

# NEW
from src_v2 import TravelPlannerV2
planner = TravelPlannerV2()
```

2. **Update invocation**:
```python
# OLD
result = agent.invoke({"messages": [{"role": "user", "content": query}]})

# NEW
result = await planner.plan_trip(query)
```

3. **Access results**:
```python
# OLD
itinerary = result["messages"][-1]["content"]

# NEW
itinerary = result["itinerary"]
flights = result["flight_options"]
```

## Roadmap

- [ ] True parallel execution of independent nodes
- [ ] Streaming support for real-time updates
- [ ] Booking and payment integration
- [ ] Multi-city trip planning
- [ ] Calendar integration
- [ ] Price alerts and notifications
- [ ] User preference learning

## Contributing

To add new features:

1. Create node in `nodes/`
2. Update state schema in `schemas/state.py`
3. Add to workflow in `workflows/travel_workflow.py`
4. Add tests
5. Update documentation

## License

MIT

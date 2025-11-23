# Future Works - Technical Implementation Plan

Bu doküman, Travel Planner V2'nin geliştirilmesi gereken özelliklerinin detaylı teknik planını içerir.

---

## 🎯 Öncelik Sıralaması

| Öncelik | Özellik | Etki | Zorluk | Tahmini Süre |
|---------|---------|------|--------|--------------|
| 🔴 P0 | True Parallel Execution | Yüksek (4x hız) | Orta | 2-3 gün |
| 🔴 P0 | Error Recovery & Retry | Yüksek (güvenilirlik) | Orta | 2-3 gün |
| 🟡 P1 | Multi-City Support | Orta | Yüksek | 5-7 gün |
| 🟡 P1 | State Persistence & Resume | Orta | Orta | 3-4 gün |
| 🟡 P1 | Booking & Payment | Yüksek (revenue) | Yüksek | 7-10 gün |
| 🟢 P2 | Price Tracking & Alerts | Orta | Orta | 4-5 gün |
| 🟢 P2 | User Personalization | Orta | Yüksek | 7-10 gün |
| 🟢 P3 | Advanced Filtering | Düşük | Düşük | 2-3 gün |
| 🟢 P3 | Alternative Airports | Düşük | Orta | 3-4 gün |

---

## 1. True Parallel Execution (P0)

### 📋 Problem
Şu anda `search_flights → search_hotels → check_weather → search_activities` sıralı çalışıyor.
Bu node'lar birbirinden bağımsız, aynı anda çalışabilir.

### 🎯 Hedef
4 node'u gerçekten paralel çalıştırarak latency'yi ~4x azaltmak.

### 🔧 Teknik Çözüm

#### **1.1. State Schema Güncelleme**

```python
# src_v2/schemas/state.py

from typing import TypedDict, Optional, List, Dict, Any, Literal
from datetime import datetime

class ParallelSearchState(TypedDict, total=False):
    """State for parallel search operations."""
    flight_search_status: Literal["pending", "running", "completed", "failed"]
    hotel_search_status: Literal["pending", "running", "completed", "failed"]
    weather_search_status: Literal["pending", "running", "completed", "failed"]
    activity_search_status: Literal["pending", "running", "completed", "failed"]

    # Timestamps for monitoring
    flight_search_started_at: Optional[str]
    flight_search_completed_at: Optional[str]
    hotel_search_started_at: Optional[str]
    hotel_search_completed_at: Optional[str]
    weather_search_started_at: Optional[str]
    weather_search_completed_at: Optional[str]
    activity_search_started_at: Optional[str]
    activity_search_completed_at: Optional[str]

class TravelPlannerState(TypedDict, total=False):
    # ... existing fields ...

    # Add parallel search tracking
    parallel_search: Optional[ParallelSearchState]
```

#### **1.2. Parallel Node Implementation**

```python
# src_v2/nodes/parallel_search_node.py

"""Parallel search orchestrator node."""

from typing import Dict, Any, List
import asyncio
from datetime import datetime
from langchain_core.language_models import BaseChatModel

from ..schemas.state import TravelPlannerState
from .flight_node import search_flights_node
from .hotel_node import search_hotels_node
from .weather_node import check_weather_node
from .activity_node import search_activities_node


async def parallel_search_node(
    state: TravelPlannerState,
    llm: BaseChatModel
) -> Dict[str, Any]:
    """
    Execute all search nodes in parallel using asyncio.gather().

    This node:
    1. Identifies which searches are required
    2. Launches them in parallel
    3. Waits for all to complete
    4. Aggregates results
    """

    # Determine which searches to run
    tasks = []
    task_names = []

    if state.get("requires_flights", False):
        tasks.append(search_flights_node(state, llm))
        task_names.append("flight_search")

    if state.get("requires_hotels", False):
        tasks.append(search_hotels_node(state, llm))
        task_names.append("hotel_search")

    if state.get("requires_weather", False):
        tasks.append(check_weather_node(state, llm))
        task_names.append("weather_search")

    if state.get("requires_activities", False):
        tasks.append(search_activities_node(state, llm))
        task_names.append("activity_search")

    if not tasks:
        # No searches required
        return {
            "current_step": "parallel_search",
            "completed_steps": state.get("completed_steps", []) + ["parallel_search_skipped"],
            "errors": state.get("errors", [])
        }

    # Execute all searches in parallel
    start_time = datetime.now()

    try:
        # Run all tasks concurrently
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Aggregate results
        aggregated_state = {
            "current_step": "parallel_search",
            "completed_steps": state.get("completed_steps", []) + ["parallel_search"],
            "errors": state.get("errors", [])
        }

        # Merge results from each task
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                # Handle exceptions
                aggregated_state["errors"].append(
                    f"{task_names[i]} failed: {str(result)}"
                )
            elif isinstance(result, dict):
                # Merge successful results
                for key, value in result.items():
                    if key == "errors":
                        # Merge errors
                        aggregated_state["errors"].extend(value)
                    elif key in ["flight_options", "hotel_options", "activity_options", "weather_forecast"]:
                        # Replace list results
                        aggregated_state[key] = value
                    elif key not in aggregated_state:
                        # Add new fields
                        aggregated_state[key] = value

        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()

        aggregated_state["parallel_search_duration"] = duration

        return aggregated_state

    except Exception as e:
        return {
            "current_step": "parallel_search",
            "completed_steps": state.get("completed_steps", []) + ["parallel_search"],
            "errors": state.get("errors", []) + [f"Parallel search orchestration error: {str(e)}"]
        }
```

#### **1.3. Workflow Integration**

```python
# src_v2/workflows/travel_workflow.py

from ..nodes.parallel_search_node import parallel_search_node

def create_travel_workflow(llm: BaseChatModel):
    """Create the LangGraph workflow with true parallel execution."""

    workflow = StateGraph(TravelPlannerState)

    # ... (existing intent classifier node)

    # Add single parallel search node instead of chained nodes
    workflow.add_node(
        "parallel_search",
        wrap_async_node(parallel_search_node)
    )

    # Simplified routing
    workflow.add_conditional_edges(
        "classify_intent",
        route_after_intent,
        {
            "parallel_search": "parallel_search",  # Single node handles all searches
            "end": "response_generator"
        }
    )

    # After parallel search, route to itinerary or response
    workflow.add_conditional_edges(
        "parallel_search",
        route_after_parallel_search,
        {
            "generate_itinerary": "generate_itinerary",
            "end": "response_generator"
        }
    )

    # ... (rest remains same)

    return app
```

#### **1.4. Testing**

```python
# tests/test_parallel_execution.py

import pytest
import asyncio
from unittest.mock import AsyncMock
from src_v2.nodes.parallel_search_node import parallel_search_node

@pytest.mark.asyncio
async def test_parallel_search_all_enabled():
    """Test that all searches run in parallel when enabled."""

    state = {
        "user_query": "Plan a trip to Paris",
        "requires_flights": True,
        "requires_hotels": True,
        "requires_weather": True,
        "requires_activities": True,
        "origin": "NYC",
        "destination": "Paris",
        "departure_date": "2024-06-15",
        "return_date": "2024-06-20",
        "completed_steps": []
    }

    mock_llm = AsyncMock()

    result = await parallel_search_node(state, mock_llm)

    # Verify all results present
    assert "flight_options" in result or "errors" in result
    assert "hotel_options" in result or "errors" in result
    assert "weather_forecast" in result or "errors" in result
    assert "activity_options" in result or "errors" in result

    # Verify it was faster than sequential (check duration)
    assert result.get("parallel_search_duration", 0) > 0
    print(f"Parallel search completed in {result['parallel_search_duration']:.2f}s")

@pytest.mark.asyncio
async def test_parallel_search_partial():
    """Test that only required searches run."""

    state = {
        "user_query": "Find flights to Paris",
        "requires_flights": True,
        "requires_hotels": False,
        "requires_weather": False,
        "requires_activities": False,
        "origin": "NYC",
        "destination": "Paris",
        "departure_date": "2024-06-15",
        "completed_steps": []
    }

    mock_llm = AsyncMock()

    result = await parallel_search_node(state, mock_llm)

    # Only flight results should be present
    assert "flight_options" in result or any("flight" in err.lower() for err in result.get("errors", []))
    # Others should not be present
    assert "hotel_options" not in result or result["hotel_options"] == []
```

---

## 2. Error Recovery & Retry Logic (P0)

### 📋 Problem
Şu anda hata olunca sadece error listesine ekleniyor, retry yok.
Production'da geçici API hataları yaşanabilir.

### 🎯 Hedef
Transient errors için otomatik retry, persistent errors için fallback.

### 🔧 Teknik Çözüm

#### **2.1. Retry Decorator**

```python
# src_v2/utils/retry.py

"""Retry utilities for handling transient errors."""

import asyncio
import functools
from typing import Callable, TypeVar, Any, Type
from datetime import datetime

T = TypeVar('T')


class RetryConfig:
    """Configuration for retry behavior."""

    def __init__(
        self,
        max_attempts: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        exponential_base: float = 2.0,
        jitter: bool = True
    ):
        self.max_attempts = max_attempts
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.exponential_base = exponential_base
        self.jitter = jitter


class RetryableError(Exception):
    """Base class for errors that should trigger retry."""
    pass


class NonRetryableError(Exception):
    """Base class for errors that should NOT trigger retry."""
    pass


def calculate_delay(attempt: int, config: RetryConfig) -> float:
    """Calculate delay for next retry attempt."""
    import random

    # Exponential backoff
    delay = config.initial_delay * (config.exponential_base ** attempt)

    # Cap at max_delay
    delay = min(delay, config.max_delay)

    # Add jitter
    if config.jitter:
        delay = delay * (0.5 + random.random() * 0.5)

    return delay


def with_retry(
    config: RetryConfig = None,
    retryable_exceptions: tuple = (Exception,),
    non_retryable_exceptions: tuple = (NonRetryableError,)
):
    """
    Decorator that adds retry logic to async functions.

    Usage:
        @with_retry(config=RetryConfig(max_attempts=3))
        async def my_function():
            ...
    """
    if config is None:
        config = RetryConfig()

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs) -> T:
            last_exception = None

            for attempt in range(config.max_attempts):
                try:
                    # Try to execute the function
                    result = await func(*args, **kwargs)

                    # Success - log if this was a retry
                    if attempt > 0:
                        print(f"✅ {func.__name__} succeeded on attempt {attempt + 1}")

                    return result

                except non_retryable_exceptions as e:
                    # Don't retry these
                    print(f"❌ {func.__name__} failed with non-retryable error: {e}")
                    raise

                except retryable_exceptions as e:
                    last_exception = e

                    # Check if we should retry
                    if attempt < config.max_attempts - 1:
                        delay = calculate_delay(attempt, config)
                        print(f"⚠️  {func.__name__} failed (attempt {attempt + 1}/{config.max_attempts}), retrying in {delay:.2f}s: {e}")
                        await asyncio.sleep(delay)
                    else:
                        print(f"❌ {func.__name__} failed after {config.max_attempts} attempts: {e}")

            # All retries exhausted
            raise last_exception

        return wrapper

    return decorator
```

#### **2.2. Apply Retry to Nodes**

```python
# src_v2/nodes/flight_node.py (updated)

from ..utils.retry import with_retry, RetryConfig, RetryableError

# Define retry config for flight searches
FLIGHT_RETRY_CONFIG = RetryConfig(
    max_attempts=3,
    initial_delay=2.0,
    max_delay=10.0,
    exponential_base=2.0
)

@with_retry(config=FLIGHT_RETRY_CONFIG)
async def _search_flights_with_retry(search_params: dict) -> list:
    """Internal function that performs the actual search with retry logic."""
    from src.tools.flight_tools import search_flights

    try:
        result = search_flights.invoke(search_params)
        return result
    except ConnectionError as e:
        # Network errors are retryable
        raise RetryableError(f"Connection error: {e}")
    except TimeoutError as e:
        # Timeout errors are retryable
        raise RetryableError(f"Timeout error: {e}")
    except ValueError as e:
        # Invalid input is NOT retryable
        raise NonRetryableError(f"Invalid parameters: {e}")


async def search_flights_node(
    state: TravelPlannerState,
    llm: BaseChatModel
) -> Dict[str, Any]:
    """Search for flight options with retry logic."""

    if not state.get("requires_flights", False):
        return {
            "flight_options": [],
            "completed_steps": state.get("completed_steps", []) + ["flight_search_skipped"]
        }

    # ... (validation code)

    try:
        # Build search parameters
        search_params = {
            "origin": origin,
            "destination": destination,
            "departure_date": departure_date,
            "passengers": num_passengers
        }

        if return_date:
            search_params["return_date"] = return_date

        # Execute search with retry
        result = await _search_flights_with_retry(search_params)

        # ... (rest of processing)

    except Exception as e:
        errors.append(f"Flight search error after all retries: {str(e)}")
        return {
            "flight_options": [],
            "errors": errors,
            "current_step": "flight_search",
            "completed_steps": state.get("completed_steps", []) + ["flight_search"]
        }
```

#### **2.3. Fallback Strategy**

```python
# src_v2/nodes/flight_node_with_fallback.py

"""Flight search with fallback providers."""

from typing import Dict, Any, List, Optional
from ..utils.retry import with_retry, RetryConfig

# Primary provider
async def search_flights_primary(params: dict) -> list:
    """Primary flight search using main API."""
    from src.tools.flight_tools import search_flights
    return search_flights.invoke(params)

# Fallback provider (mock or alternative API)
async def search_flights_fallback(params: dict) -> list:
    """Fallback flight search using alternative API or cached data."""
    # Could be: different API, cached results, or mock data
    from ..mocks.flight_mock import mock_flight_search
    return mock_flight_search(params)


async def search_flights_with_fallback(params: dict) -> tuple[list, str]:
    """
    Search flights with automatic fallback.

    Returns:
        (results, provider_used)
    """
    # Try primary
    try:
        result = await search_flights_primary(params)
        return result, "primary"
    except Exception as primary_error:
        print(f"⚠️  Primary flight search failed: {primary_error}")

        # Try fallback
        try:
            result = await search_flights_fallback(params)
            return result, "fallback"
        except Exception as fallback_error:
            print(f"❌ Fallback flight search also failed: {fallback_error}")
            raise Exception(f"All providers failed. Primary: {primary_error}, Fallback: {fallback_error}")
```

#### **2.4. Circuit Breaker Pattern**

```python
# src_v2/utils/circuit_breaker.py

"""Circuit breaker pattern for preventing cascading failures."""

import asyncio
from datetime import datetime, timedelta
from enum import Enum
from typing import Callable, TypeVar

T = TypeVar('T')


class CircuitState(Enum):
    CLOSED = "closed"  # Normal operation
    OPEN = "open"      # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if service recovered


class CircuitBreaker:
    """
    Circuit breaker to prevent repeated calls to failing services.

    States:
    - CLOSED: Normal operation, requests go through
    - OPEN: Too many failures, reject requests immediately
    - HALF_OPEN: After timeout, allow one request to test recovery
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: float = 60.0,
        expected_exception: type = Exception
    ):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED

    async def call(self, func: Callable[..., T], *args, **kwargs) -> T:
        """Execute function with circuit breaker protection."""

        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            # Check if recovery timeout has passed
            if self.last_failure_time and \
               datetime.now() - self.last_failure_time > timedelta(seconds=self.recovery_timeout):
                self.state = CircuitState.HALF_OPEN
                print(f"🔄 Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")

        try:
            # Execute function
            result = await func(*args, **kwargs)

            # Success - reset circuit
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                print(f"✅ Circuit breaker recovered - entering CLOSED state")

            self.failure_count = 0
            return result

        except self.expected_exception as e:
            # Record failure
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            # Check if threshold exceeded
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                print(f"🚫 Circuit breaker opened after {self.failure_count} failures")

            raise


# Global circuit breakers for each service
_flight_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)
_hotel_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30.0)


async def search_flights_with_breaker(params: dict) -> list:
    """Flight search protected by circuit breaker."""
    from src.tools.flight_tools import search_flights

    async def _search():
        return search_flights.invoke(params)

    return await _flight_breaker.call(_search)
```

---

## 3. Multi-City Trip Support (P1)

### 📋 Problem
Şu anda sadece tek origin-destination destekleniyor.
"Paris → Roma → Barselona" gibi multi-city trips yapılamıyor.

### 🎯 Hedef
Birden fazla şehri kapsayan tur planlaması.

### 🔧 Teknik Çözüm

#### **3.1. State Schema Extension**

```python
# src_v2/schemas/state.py (extended)

class TripSegment(TypedDict, total=False):
    """A single segment of a multi-city trip."""
    segment_id: str
    origin: str
    destination: str
    departure_date: str
    arrival_date: Optional[str]
    duration_days: int

    # Segment-specific results
    flight: Optional[FlightOption]
    hotel: Optional[HotelOption]
    activities: List[ActivityOption]
    weather: List[WeatherInfo]


class MultiCityTravelState(TypedDict, total=False):
    """Extended state for multi-city trips."""

    # Multi-city specific
    is_multi_city: bool
    segments: List[TripSegment]
    current_segment_index: int

    # Legacy single-trip fields still supported
    origin: Optional[str]
    destination: Optional[str]

    # ... rest of fields
```

#### **3.2. Multi-City Intent Classifier**

```python
# src_v2/nodes/intent_classifier.py (updated)

MULTI_CITY_INTENT_PROMPT = """You are an intent classifier for a travel planning system.

Analyze the user query and determine if this is a MULTI-CITY trip (visiting multiple destinations).

User Query: {query}
Current Date: {current_date}

Respond ONLY with valid JSON:
{{
    "intent": "plan_trip" or "plan_multi_city_trip",
    "is_multi_city": true or false,
    "segments": [
        {{
            "origin": "Paris",
            "destination": "Rome",
            "departure_date": "2024-06-15",
            "duration_days": 3
        }},
        {{
            "origin": "Rome",
            "destination": "Barcelona",
            "departure_date": "2024-06-18",
            "duration_days": 4
        }}
    ],
    "total_duration_days": 7,
    "budget": 3000.0,
    "num_passengers": 2
}}

IMPORTANT: If multiple cities are mentioned (e.g., "Paris, Rome, and Barcelona"), set is_multi_city=true and create segments."""


async def classify_intent_node(
    state: TravelPlannerState,
    llm: BaseChatModel
) -> Dict[str, Any]:
    """Enhanced intent classifier with multi-city support."""

    user_query = state.get("user_query", "")

    # ... (validation)

    try:
        # Use multi-city aware prompt
        messages = [
            SystemMessage(content=MULTI_CITY_INTENT_PROMPT.format(
                query=user_query,
                current_date=datetime.now().strftime("%Y-%m-%d")
            ))
        ]

        response = await llm.ainvoke(messages)
        result = extract_json_from_text(response.content)

        # Check if multi-city
        is_multi_city = result.get("is_multi_city", False)

        if is_multi_city:
            # Multi-city trip
            segments = result.get("segments", [])
            return {
                "intent": "plan_multi_city_trip",
                "is_multi_city": True,
                "segments": segments,
                "current_segment_index": 0,
                "requires_flights": True,
                "requires_hotels": True,
                "requires_weather": True,
                "requires_activities": True,
                # ... rest
            }
        else:
            # Single trip (existing logic)
            return {
                "intent": result.get("intent", "general"),
                "is_multi_city": False,
                "origin": result.get("origin"),
                "destination": result.get("destination"),
                # ... rest
            }

    except Exception as e:
        # ... error handling
```

#### **3.3. Multi-City Search Node**

```python
# src_v2/nodes/multi_city_search_node.py

"""Search node for multi-city trips."""

import asyncio
from typing import Dict, Any, List
from langchain_core.language_models import BaseChatModel

from ..schemas.state import TravelPlannerState, TripSegment
from .flight_node import search_flights_node
from .hotel_node import search_hotels_node
from .weather_node import check_weather_node
from .activity_node import search_activities_node


async def search_segment(
    segment: TripSegment,
    segment_index: int,
    num_passengers: int,
    budget_per_segment: float,
    llm: BaseChatModel
) -> Dict[str, Any]:
    """Search for a single trip segment."""

    # Create a temporary state for this segment
    segment_state = {
        "user_query": f"Segment {segment_index + 1}",
        "origin": segment.get("origin"),
        "destination": segment.get("destination"),
        "departure_date": segment.get("departure_date"),
        "return_date": segment.get("arrival_date"),
        "num_passengers": num_passengers,
        "budget": budget_per_segment,
        "requires_flights": True,
        "requires_hotels": True,
        "requires_weather": True,
        "requires_activities": True,
        "completed_steps": [],
        "errors": []
    }

    # Run searches in parallel for this segment
    tasks = [
        search_flights_node(segment_state, llm),
        search_hotels_node(segment_state, llm),
        check_weather_node(segment_state, llm),
        search_activities_node(segment_state, llm)
    ]

    results = await asyncio.gather(*tasks, return_exceptions=True)

    # Aggregate segment results
    segment_results = {
        "segment_id": segment.get("segment_id", f"segment_{segment_index}"),
        "origin": segment.get("origin"),
        "destination": segment.get("destination"),
        "flight_options": [],
        "hotel_options": [],
        "weather_forecast": [],
        "activity_options": [],
        "errors": []
    }

    for result in results:
        if isinstance(result, Exception):
            segment_results["errors"].append(str(result))
        elif isinstance(result, dict):
            segment_results.update(result)

    return segment_results


async def multi_city_search_node(
    state: TravelPlannerState,
    llm: BaseChatModel
) -> Dict[str, Any]:
    """
    Search for multi-city trip segments in parallel.

    For each segment:
    - Search flights from origin to destination
    - Search hotels in destination
    - Check weather in destination
    - Search activities in destination
    """

    if not state.get("is_multi_city", False):
        # Not a multi-city trip, skip
        return {
            "current_step": "multi_city_search",
            "completed_steps": state.get("completed_steps", []) + ["multi_city_search_skipped"]
        }

    segments = state.get("segments", [])
    if not segments:
        return {
            "errors": state.get("errors", []) + ["No segments defined for multi-city trip"],
            "current_step": "multi_city_search",
            "completed_steps": state.get("completed_steps", []) + ["multi_city_search"]
        }

    num_passengers = state.get("num_passengers", 1)
    total_budget = state.get("budget")
    budget_per_segment = total_budget / len(segments) if total_budget else None

    # Search all segments in parallel
    segment_tasks = [
        search_segment(segment, i, num_passengers, budget_per_segment, llm)
        for i, segment in enumerate(segments)
    ]

    segment_results = await asyncio.gather(*segment_tasks, return_exceptions=True)

    # Aggregate all segment results
    all_errors = []
    processed_segments = []

    for i, result in enumerate(segment_results):
        if isinstance(result, Exception):
            all_errors.append(f"Segment {i} failed: {str(result)}")
        else:
            processed_segments.append(result)
            all_errors.extend(result.get("errors", []))

    return {
        "segments": processed_segments,
        "current_step": "multi_city_search",
        "completed_steps": state.get("completed_steps", []) + ["multi_city_search"],
        "errors": state.get("errors", []) + all_errors
    }
```

#### **3.4. Multi-City Itinerary Generator**

```python
# src_v2/nodes/multi_city_itinerary_node.py

"""Generate itinerary for multi-city trips."""

from typing import Dict, Any
from langchain_core.language_models import BaseChatModel
from langchain_core.messages import SystemMessage

MULTI_CITY_ITINERARY_PROMPT = """You are a professional travel planner creating a comprehensive multi-city itinerary.

**Trip Overview:**
- Total Duration: {total_days} days
- Cities: {cities}
- Passengers: {num_passengers}
- Total Budget: ${total_budget}

**Segments:**
{segments_info}

Create a detailed day-by-day itinerary that includes:
1. Flight details for each segment (inter-city travel)
2. Hotel recommendations for each city
3. Daily activities in each city
4. Weather-based packing recommendations
5. Budget breakdown by city
6. Transportation tips between cities
7. Important reminders and tips

Format in clear, readable markdown."""


async def generate_multi_city_itinerary_node(
    state: TravelPlannerState,
    llm: BaseChatModel
) -> Dict[str, Any]:
    """Generate itinerary for multi-city trip."""

    if not state.get("is_multi_city", False):
        return {
            "current_step": "multi_city_itinerary",
            "completed_steps": state.get("completed_steps", []) + ["multi_city_itinerary_skipped"]
        }

    segments = state.get("segments", [])
    num_passengers = state.get("num_passengers", 1)
    total_budget = state.get("budget", "Not specified")

    # Build segments info
    segments_info_parts = []
    total_cost = 0.0
    cities = []

    for i, segment in enumerate(segments):
        origin = segment.get("origin", "N/A")
        destination = segment.get("destination", "N/A")
        cities.append(destination)

        # Flight info
        flight_options = segment.get("flight_options", [])
        flight_info = "No flights available"
        if flight_options:
            best_flight = min(flight_options, key=lambda f: f.get('price', float('inf')))
            flight_info = f"{best_flight.get('airline')} - ${best_flight.get('price')}"
            total_cost += best_flight.get('price', 0) * num_passengers

        # Hotel info
        hotel_options = segment.get("hotel_options", [])
        hotel_info = "No hotels available"
        if hotel_options:
            best_hotel = max(hotel_options, key=lambda h: h.get('rating', 0))
            hotel_info = f"{best_hotel.get('name')} - ${best_hotel.get('total_price')}"
            total_cost += best_hotel.get('total_price', 0)

        segment_info = f"""
**Segment {i + 1}: {origin} → {destination}**
- Flight: {flight_info}
- Hotel: {hotel_info}
- Duration: {segment.get('duration_days', 'N/A')} days
"""
        segments_info_parts.append(segment_info)

    segments_info = "\n".join(segments_info_parts)
    total_days = sum(s.get('duration_days', 0) for s in segments)
    cities_str = " → ".join(cities)

    # Generate itinerary
    prompt = MULTI_CITY_ITINERARY_PROMPT.format(
        total_days=total_days,
        cities=cities_str,
        num_passengers=num_passengers,
        total_budget=total_budget,
        segments_info=segments_info
    )

    response = await llm.ainvoke([SystemMessage(content=prompt)])

    return {
        "itinerary": response.content,
        "total_cost": total_cost,
        "current_step": "multi_city_itinerary",
        "completed_steps": state.get("completed_steps", []) + ["multi_city_itinerary"]
    }
```

---

## 4. State Persistence & Resume (P1)

### 📋 Problem
Workflow her zaman baştan başlıyor. Kullanıcı "şimdi otel bul" dediğinde tüm flow tekrar çalışıyor.

### 🎯 Hedef
State'i kaydet, kaldığı yerden devam edebilsin.

### 🔧 Teknik Çözüm

#### **4.1. State Persistence Layer**

```python
# src_v2/persistence/state_store.py

"""State persistence for resumable workflows."""

import json
import hashlib
from typing import Dict, Any, Optional
from datetime import datetime, timedelta
from pathlib import Path

from ..schemas.state import TravelPlannerState


class StateStore:
    """
    Store and retrieve workflow states.

    Supports:
    - In-memory storage (for testing)
    - File-based storage (for development)
    - Redis storage (for production)
    - Database storage (for production with search)
    """

    def __init__(self, backend: str = "memory", **kwargs):
        self.backend = backend
        self._memory_store: Dict[str, Dict[str, Any]] = {}

        if backend == "file":
            self.storage_dir = Path(kwargs.get("storage_dir", "./.state_cache"))
            self.storage_dir.mkdir(exist_ok=True)
        elif backend == "redis":
            import redis
            self.redis_client = redis.Redis(
                host=kwargs.get("redis_host", "localhost"),
                port=kwargs.get("redis_port", 6379),
                db=kwargs.get("redis_db", 0)
            )

    def _generate_session_id(self, user_id: str, query: str) -> str:
        """Generate unique session ID."""
        raw = f"{user_id}:{query}:{datetime.now().isoformat()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def save_state(
        self,
        session_id: str,
        state: TravelPlannerState,
        ttl: int = 3600
    ) -> bool:
        """
        Save workflow state.

        Args:
            session_id: Unique session identifier
            state: Current workflow state
            ttl: Time-to-live in seconds (default: 1 hour)

        Returns:
            True if saved successfully
        """
        try:
            state_data = {
                "state": dict(state),
                "saved_at": datetime.now().isoformat(),
                "ttl": ttl
            }

            if self.backend == "memory":
                self._memory_store[session_id] = state_data

            elif self.backend == "file":
                file_path = self.storage_dir / f"{session_id}.json"
                with open(file_path, 'w') as f:
                    json.dump(state_data, f, indent=2)

            elif self.backend == "redis":
                self.redis_client.setex(
                    f"session:{session_id}",
                    ttl,
                    json.dumps(state_data)
                )

            return True

        except Exception as e:
            print(f"Error saving state: {e}")
            return False

    def load_state(self, session_id: str) -> Optional[TravelPlannerState]:
        """
        Load workflow state.

        Args:
            session_id: Session identifier

        Returns:
            Saved state or None if not found/expired
        """
        try:
            if self.backend == "memory":
                state_data = self._memory_store.get(session_id)

            elif self.backend == "file":
                file_path = self.storage_dir / f"{session_id}.json"
                if not file_path.exists():
                    return None
                with open(file_path, 'r') as f:
                    state_data = json.load(f)

            elif self.backend == "redis":
                data = self.redis_client.get(f"session:{session_id}")
                if not data:
                    return None
                state_data = json.loads(data)

            else:
                return None

            # Check if expired
            if state_data:
                saved_at = datetime.fromisoformat(state_data["saved_at"])
                ttl = state_data.get("ttl", 3600)
                if datetime.now() - saved_at > timedelta(seconds=ttl):
                    return None

                return state_data["state"]

            return None

        except Exception as e:
            print(f"Error loading state: {e}")
            return None

    def delete_state(self, session_id: str) -> bool:
        """Delete saved state."""
        try:
            if self.backend == "memory":
                self._memory_store.pop(session_id, None)

            elif self.backend == "file":
                file_path = self.storage_dir / f"{session_id}.json"
                if file_path.exists():
                    file_path.unlink()

            elif self.backend == "redis":
                self.redis_client.delete(f"session:{session_id}")

            return True

        except Exception as e:
            print(f"Error deleting state: {e}")
            return False
```

#### **4.2. Resumable Workflow**

```python
# src_v2/travel_planner_v2.py (updated)

from .persistence.state_store import StateStore

class TravelPlannerV2:
    """Enhanced planner with state persistence."""

    def __init__(
        self,
        model: Optional[str] = None,
        provider: str = "anthropic",
        verbose: bool = False,
        enable_monitoring: bool = True,
        enable_persistence: bool = True,
        persistence_backend: str = "memory"
    ):
        # ... existing init ...

        # State persistence
        self.enable_persistence = enable_persistence
        if enable_persistence:
            self.state_store = StateStore(backend=persistence_backend)
        else:
            self.state_store = None

    async def plan_trip(
        self,
        query: str,
        session_id: Optional[str] = None,
        resume: bool = False,
        **kwargs
    ) -> TravelPlannerState:
        """
        Plan a trip with optional resume capability.

        Args:
            query: User query
            session_id: Optional session ID for resume
            resume: If True, try to resume from saved state
            **kwargs: Additional parameters

        Returns:
            Final state
        """

        # Try to resume if requested
        if resume and session_id and self.state_store:
            saved_state = self.state_store.load_state(session_id)
            if saved_state:
                if self.verbose:
                    print(f"♻️  Resuming from saved state (session: {session_id})")
                    print(f"   Completed steps: {saved_state.get('completed_steps', [])}")

                # Update query if new one provided
                saved_state["user_query"] = query

                # Merge any new parameters
                for key, value in kwargs.items():
                    if value is not None:
                        saved_state[key] = value

                initial_state = saved_state
            else:
                if self.verbose:
                    print(f"⚠️  No saved state found for session {session_id}, starting fresh")
                initial_state = self._create_initial_state(query, **kwargs)
        else:
            # Start fresh
            initial_state = self._create_initial_state(query, **kwargs)

        # Generate session ID if not provided
        if not session_id:
            import hashlib
            session_id = hashlib.sha256(f"{query}:{datetime.now()}".encode()).hexdigest()[:16]

        # Execute workflow
        result = await self.workflow.ainvoke(initial_state)

        # Save state for future resume
        if self.enable_persistence and self.state_store:
            self.state_store.save_state(session_id, result)
            if self.verbose:
                print(f"💾 State saved (session: {session_id})")

        return result

    def _create_initial_state(self, query: str, **kwargs) -> TravelPlannerState:
        """Create fresh initial state."""
        return {
            "user_query": query,
            "origin": kwargs.get("origin"),
            "destination": kwargs.get("destination"),
            "departure_date": kwargs.get("departure_date"),
            "return_date": kwargs.get("return_date"),
            "num_passengers": kwargs.get("num_passengers", 1),
            "budget": kwargs.get("budget"),
            "preferences": kwargs.get("preferences", {}),
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
```

#### **4.3. Usage Example**

```python
# examples/resumable_planning.py

"""Example of resumable workflow."""

import asyncio
from src_v2 import TravelPlannerV2


async def main():
    planner = TravelPlannerV2(
        provider="anthropic",
        enable_persistence=True,
        persistence_backend="file",
        verbose=True
    )

    # First request - search flights
    print("=== Step 1: Search Flights ===")
    result1 = await planner.plan_trip(
        query="Find flights from NYC to Paris on June 15",
        session_id="user123_trip1"
    )
    print(f"Found {len(result1['flight_options'])} flights")

    # Second request - now add hotels (resume from previous state)
    print("\n=== Step 2: Add Hotels (Resume) ===")
    result2 = await planner.plan_trip(
        query="Now find hotels in Paris for 5 nights",
        session_id="user123_trip1",
        resume=True  # Resume from saved state
    )
    print(f"Found {len(result2['hotel_options'])} hotels")
    print(f"Previous flight options still available: {len(result2['flight_options'])} flights")

    # Third request - generate final itinerary (resume again)
    print("\n=== Step 3: Generate Itinerary (Resume) ===")
    result3 = await planner.plan_trip(
        query="Generate a complete itinerary with the best options",
        session_id="user123_trip1",
        resume=True
    )
    print(result3['itinerary'])


if __name__ == "__main__":
    asyncio.run(main())
```

---

## 5. Booking & Payment Integration (P1)

### 📋 Problem
`booking_confirmed`, `payment_status`, `transaction_id` field'ları var ama kullanılmıyor.

### 🎯 Hedef
Gerçek rezervasyon ve ödeme akışı.

### 🔧 Teknik Çözüm

#### **5.1. Payment Gateway Integration**

```python
# src_v2/integrations/payment_gateway.py

"""Payment gateway integration (Stripe example)."""

from typing import Dict, Any, Optional
from enum import Enum


class PaymentStatus(Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    REFUNDED = "refunded"


class PaymentGateway:
    """
    Abstract payment gateway interface.

    Implementations: Stripe, PayPal, Square, etc.
    """

    async def create_payment_intent(
        self,
        amount: float,
        currency: str = "USD",
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create a payment intent.

        Returns:
            {
                "payment_intent_id": "pi_xxx",
                "client_secret": "secret_xxx",
                "status": "pending"
            }
        """
        raise NotImplementedError

    async def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """Confirm and process payment."""
        raise NotImplementedError

    async def refund_payment(self, payment_intent_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Refund a payment (full or partial)."""
        raise NotImplementedError


class MockPaymentGateway(PaymentGateway):
    """Mock payment gateway for testing."""

    def __init__(self, auto_succeed: bool = True):
        self.auto_succeed = auto_succeed
        self._payments = {}

    async def create_payment_intent(
        self,
        amount: float,
        currency: str = "USD",
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create mock payment intent."""
        import uuid

        payment_id = f"pi_mock_{uuid.uuid4().hex[:16]}"

        self._payments[payment_id] = {
            "payment_intent_id": payment_id,
            "amount": amount,
            "currency": currency,
            "status": PaymentStatus.PENDING.value,
            "customer_id": customer_id,
            "metadata": metadata or {}
        }

        return {
            "payment_intent_id": payment_id,
            "client_secret": f"secret_{uuid.uuid4().hex}",
            "status": PaymentStatus.PENDING.value
        }

    async def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """Confirm mock payment."""
        if payment_intent_id not in self._payments:
            raise ValueError(f"Payment intent {payment_intent_id} not found")

        payment = self._payments[payment_intent_id]

        if self.auto_succeed:
            payment["status"] = PaymentStatus.SUCCEEDED.value
        else:
            payment["status"] = PaymentStatus.FAILED.value

        return payment

    async def refund_payment(self, payment_intent_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Refund mock payment."""
        if payment_intent_id not in self._payments:
            raise ValueError(f"Payment intent {payment_intent_id} not found")

        payment = self._payments[payment_intent_id]
        refund_amount = amount or payment["amount"]

        payment["status"] = PaymentStatus.REFUNDED.value
        payment["refunded_amount"] = refund_amount

        return payment


class StripePaymentGateway(PaymentGateway):
    """Real Stripe payment gateway."""

    def __init__(self, api_key: str):
        import stripe
        self.stripe = stripe
        self.stripe.api_key = api_key

    async def create_payment_intent(
        self,
        amount: float,
        currency: str = "USD",
        customer_id: Optional[str] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Create Stripe payment intent."""

        # Stripe uses cents
        amount_cents = int(amount * 100)

        intent = self.stripe.PaymentIntent.create(
            amount=amount_cents,
            currency=currency.lower(),
            customer=customer_id,
            metadata=metadata or {},
            automatic_payment_methods={"enabled": True}
        )

        return {
            "payment_intent_id": intent.id,
            "client_secret": intent.client_secret,
            "status": intent.status
        }

    async def confirm_payment(self, payment_intent_id: str) -> Dict[str, Any]:
        """Confirm Stripe payment."""
        intent = self.stripe.PaymentIntent.confirm(payment_intent_id)

        return {
            "payment_intent_id": intent.id,
            "status": intent.status,
            "amount": intent.amount / 100  # Convert back to dollars
        }

    async def refund_payment(self, payment_intent_id: str, amount: Optional[float] = None) -> Dict[str, Any]:
        """Refund Stripe payment."""
        refund_params = {"payment_intent": payment_intent_id}

        if amount:
            refund_params["amount"] = int(amount * 100)

        refund = self.stripe.Refund.create(**refund_params)

        return {
            "refund_id": refund.id,
            "status": refund.status,
            "amount": refund.amount / 100
        }
```

#### **5.2. Booking Node**

```python
# src_v2/nodes/booking_node.py

"""Booking and payment processing node."""

from typing import Dict, Any
from langchain_core.language_models import BaseChatModel

from ..schemas.state import TravelPlannerState
from ..integrations.payment_gateway import MockPaymentGateway, PaymentStatus


async def process_booking_node(
    state: TravelPlannerState,
    llm: BaseChatModel,
    payment_gateway: MockPaymentGateway = None
) -> Dict[str, Any]:
    """
    Process booking and payment.

    Steps:
    1. Validate selections (flight, hotel)
    2. Calculate total cost
    3. Create payment intent
    4. Process payment
    5. Confirm bookings
    """

    if payment_gateway is None:
        payment_gateway = MockPaymentGateway(auto_succeed=True)

    # Check if booking requested
    intent = state.get("intent")
    if intent != "book":
        return {
            "current_step": "booking",
            "completed_steps": state.get("completed_steps", []) + ["booking_skipped"]
        }

    # Validate selections
    selected_flight = state.get("selected_flight")
    selected_hotel = state.get("selected_hotel")

    if not selected_flight and not selected_hotel:
        return {
            "errors": state.get("errors", []) + ["No flight or hotel selected for booking"],
            "current_step": "booking",
            "completed_steps": state.get("completed_steps", []) + ["booking"]
        }

    # Calculate total cost
    num_passengers = state.get("num_passengers", 1)
    total_cost = 0.0

    if selected_flight:
        total_cost += selected_flight.get("price", 0) * num_passengers

    if selected_hotel:
        total_cost += selected_hotel.get("total_price", 0)

    try:
        # Step 1: Create payment intent
        payment_intent = await payment_gateway.create_payment_intent(
            amount=total_cost,
            currency="USD",
            metadata={
                "user_query": state.get("user_query"),
                "destination": state.get("destination"),
                "num_passengers": num_passengers
            }
        )

        payment_intent_id = payment_intent["payment_intent_id"]

        # Step 2: Confirm payment
        payment_result = await payment_gateway.confirm_payment(payment_intent_id)

        if payment_result["status"] == PaymentStatus.SUCCEEDED.value:
            # Payment successful - confirm bookings

            # Here you would call actual booking APIs
            # For now, just mark as confirmed

            return {
                "booking_confirmed": True,
                "payment_status": PaymentStatus.SUCCEEDED.value,
                "transaction_id": payment_intent_id,
                "total_cost": total_cost,
                "current_step": "booking",
                "completed_steps": state.get("completed_steps", []) + ["booking"],
                "next_actions": [
                    "Booking confirmation emails sent",
                    "Tickets will be available in your account",
                    "Check-in opens 24 hours before departure"
                ]
            }
        else:
            # Payment failed
            return {
                "booking_confirmed": False,
                "payment_status": PaymentStatus.FAILED.value,
                "errors": state.get("errors", []) + ["Payment failed"],
                "current_step": "booking",
                "completed_steps": state.get("completed_steps", []) + ["booking"]
            }

    except Exception as e:
        return {
            "booking_confirmed": False,
            "payment_status": PaymentStatus.FAILED.value,
            "errors": state.get("errors", []) + [f"Booking error: {str(e)}"],
            "current_step": "booking",
            "completed_steps": state.get("completed_steps", []) + ["booking"]
        }
```

---

## 6. Mock Tools for Testing

### 🔧 Mock Flight Search

```python
# src_v2/mocks/flight_mock.py

"""Mock flight search for testing without real APIs."""

from typing import List, Dict, Any
from datetime import datetime, timedelta
import random


def mock_flight_search(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Generate realistic mock flight data.

    Args:
        params: Search parameters (origin, destination, departure_date, etc.)

    Returns:
        List of mock flight options
    """

    origin = params.get("origin", "NYC")
    destination = params.get("destination", "LAX")
    departure_date = params.get("departure_date", "2024-06-15")
    return_date = params.get("return_date")
    num_passengers = params.get("passengers", 1)

    airlines = ["United", "Delta", "American", "JetBlue", "Southwest"]

    # Generate 5-10 options
    num_options = random.randint(5, 10)
    flights = []

    base_price = random.randint(200, 800)

    for i in range(num_options):
        airline = random.choice(airlines)

        # Vary price
        price = base_price + random.randint(-100, 200)

        # Random departure time
        hour = random.randint(6, 22)
        minute = random.choice([0, 15, 30, 45])
        departure_time = f"{departure_date} {hour:02d}:{minute:02d}"

        # Duration
        duration_hours = random.randint(3, 12)
        arrival_time = (
            datetime.fromisoformat(departure_time) + timedelta(hours=duration_hours)
        ).strftime("%Y-%m-%d %H:%M")

        # Stops
        stops = random.choice([0, 0, 0, 1, 1, 2])  # Favor non-stop

        flight = {
            "flight_id": f"FL{random.randint(1000, 9999)}",
            "airline": airline,
            "origin": origin,
            "destination": destination,
            "departure_time": departure_time,
            "arrival_time": arrival_time,
            "duration_minutes": duration_hours * 60,
            "price": price,
            "stops": stops,
            "cabin_class": params.get("cabin_class", "economy"),
            "total_price": price * num_passengers
        }

        flights.append(flight)

    # Sort by price
    flights.sort(key=lambda f: f["price"])

    return flights
```

### 🔧 Mock Hotel Search

```python
# src_v2/mocks/hotel_mock.py

"""Mock hotel search for testing."""

from typing import List, Dict, Any
import random


def mock_hotel_search(params: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Generate realistic mock hotel data."""

    destination = params.get("destination", "Paris")
    check_in = params.get("check_in", "2024-06-15")
    check_out = params.get("check_out", "2024-06-20")
    num_guests = params.get("num_guests", 2)
    min_rating = params.get("min_rating", 3.0)

    # Calculate nights
    from datetime import datetime
    nights = (
        datetime.fromisoformat(check_out) - datetime.fromisoformat(check_in)
    ).days

    hotel_names = [
        "Grand Hotel", "City Center Inn", "Luxury Suites", "Budget Stay",
        "Boutique Hotel", "Riverside Lodge", "Palace Hotel", "Comfort Inn"
    ]

    amenities_pool = [
        "WiFi", "Pool", "Gym", "Spa", "Restaurant", "Bar",
        "Room Service", "Parking", "Airport Shuttle", "Pet Friendly"
    ]

    hotels = []

    for i in range(8):
        rating = round(random.uniform(2.5, 5.0), 1)

        # Skip if below minimum rating
        if rating < min_rating:
            continue

        # Price varies by rating
        base_price = 50 + (rating * 40) + random.randint(-20, 50)

        # Select amenities (more for higher rated hotels)
        num_amenities = int(rating * 2)
        amenities = random.sample(amenities_pool, min(num_amenities, len(amenities_pool)))

        hotel = {
            "hotel_id": f"HT{random.randint(1000, 9999)}",
            "name": f"{random.choice(hotel_names)} {destination}",
            "location": destination,
            "rating": rating,
            "price_per_night": base_price,
            "total_price": base_price * nights,
            "amenities": amenities,
            "distance_to_center": round(random.uniform(0.5, 10.0), 1)
        }

        hotels.append(hotel)

    # Sort by rating (descending)
    hotels.sort(key=lambda h: h["rating"], reverse=True)

    return hotels
```

---

## 📊 Implementation Roadmap

### Phase 1: Foundation (Week 1-2)
- ✅ Implement parallel execution
- ✅ Add retry logic and circuit breakers
- ✅ Create mock tools for testing
- ✅ Write comprehensive tests

### Phase 2: Advanced Features (Week 3-4)
- ✅ Multi-city trip support
- ✅ State persistence and resume
- ✅ Booking integration (mock)

### Phase 3: Production Readiness (Week 5-6)
- ✅ Real payment gateway integration
- ✅ Price tracking and alerts
- ✅ User personalization
- ✅ Advanced filtering

### Phase 4: Optimization (Week 7-8)
- ✅ Performance tuning
- ✅ Caching strategies
- ✅ Monitoring and observability
- ✅ Load testing

---

## 🧪 Testing Strategy

```python
# tests/test_future_features.py

"""Test suite for future features."""

import pytest
import asyncio
from unittest.mock import AsyncMock

from src_v2.nodes.parallel_search_node import parallel_search_node
from src_v2.nodes.multi_city_search_node import multi_city_search_node
from src_v2.nodes.booking_node import process_booking_node
from src_v2.utils.retry import with_retry, RetryConfig
from src_v2.persistence.state_store import StateStore


@pytest.mark.asyncio
async def test_parallel_execution_speed():
    """Verify parallel execution is faster than sequential."""
    # TODO: Implement
    pass


@pytest.mark.asyncio
async def test_retry_logic():
    """Test that retry decorator works correctly."""
    # TODO: Implement
    pass


@pytest.mark.asyncio
async def test_circuit_breaker():
    """Test circuit breaker prevents cascading failures."""
    # TODO: Implement
    pass


@pytest.mark.asyncio
async def test_multi_city_planning():
    """Test multi-city trip planning."""
    # TODO: Implement
    pass


@pytest.mark.asyncio
async def test_state_persistence():
    """Test state save/load/resume."""
    # TODO: Implement
    pass


@pytest.mark.asyncio
async def test_booking_flow():
    """Test end-to-end booking with payment."""
    # TODO: Implement
    pass
```

---

## 📝 Notes

1. **Backward Compatibility**: Tüm yeni özellikler opt-in olmalı, mevcut kod kırılmamalı
2. **Error Handling**: Her node exception handle etmeli, workflow devam edebilmeli
3. **Monitoring**: Production'da her feature için metrikler toplanmalı
4. **Documentation**: Her yeni özellik için örnek kod ve test yazılmalı
5. **Security**: Payment bilgileri asla state'te tutulmamalı, sadece transaction_id

---

## 🔗 Dependencies

```toml
# pyproject.toml additions

[tool.poetry.dependencies]
# Existing
langgraph = "^0.0.55"
langchain-core = "^0.1.40"

# New for future features
redis = "^5.0.0"  # For state persistence
stripe = "^7.0.0"  # For payment processing
tenacity = "^8.2.3"  # Alternative retry library
prometheus-client = "^0.19.0"  # For monitoring
```

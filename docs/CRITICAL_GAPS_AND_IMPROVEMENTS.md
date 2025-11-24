# Critical Gaps and Improvements for Travel Planner V2

**Document Version:** 1.0.0
**Date:** 2025-11-24
**Status:** 🔴 CRITICAL - Must Address Before Production

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [Critical Gaps (P0)](#critical-gaps-p0)
3. [High Priority Gaps (P1)](#high-priority-gaps-p1)
4. [Medium Priority Gaps (P2)](#medium-priority-gaps-p2)
5. [Implementation Roadmap](#implementation-roadmap)
6. [Testing Requirements](#testing-requirements)

---

## Executive Summary

### Current Status: MVP Ready ⚠️ Production Not Ready

**Overall Assessment:**
- ✅ Architecture: Excellent (9/10)
- ⚠️ Security: Needs Work (6/10)
- ⚠️ Reliability: Needs Work (7/10)
- ⚠️ Scalability: Needs Work (6/10)
- ⚠️ Observability: Basic (7/10)

**Must-Fix Before Production:** 5 critical issues
**Should-Fix Within 30 Days:** 8 high-priority issues
**Nice-to-Have:** 12 medium-priority improvements

---

## Critical Gaps (P0)

### 🔴 1. Input Validation Yetersiz

**Current State:**
```python
# travel_planner_v2.py:106-127
async def plan_trip(self, query: str, origin: Optional[str] = None, ...):
    initial_state: TravelPlannerState = {
        "user_query": query,  # ❌ NO VALIDATION!
        "origin": origin,      # ❌ NO VALIDATION!
        ...
    }
```

**Problems:**
1. ❌ **Query length kontrolü yok** → DOS attack riski
2. ❌ **Empty/null query kontrolü yok** → Runtime errors
3. ❌ **Malicious input filtreleme yok** → Prompt injection
4. ❌ **Special characters sanitization yok** → XSS, SQL injection
5. ❌ **Date format validation yok** → Invalid date parsing
6. ❌ **Budget range validation yok** → Negative/extreme values
7. ❌ **Passenger count validation yok** → 0 or 10000 passengers

**Impact:**
- 🔴 **Security Risk:** HIGH - Prompt injection, XSS attacks
- 🔴 **Stability Risk:** HIGH - System crashes on invalid input
- 🔴 **Cost Risk:** HIGH - Excessive LLM token usage from long queries

**Solution:**

**Step 1: Create Validation Module**

Create `src_v2/validators/input_validator.py`:

```python
"""Input validation for travel planner."""

from typing import Optional, Dict, Any
from datetime import datetime
import re
from pydantic import BaseModel, validator, Field


class TravelQueryValidator(BaseModel):
    """Validator for travel planning queries."""

    query: str = Field(..., min_length=3, max_length=1000)
    origin: Optional[str] = Field(None, min_length=2, max_length=100)
    destination: Optional[str] = Field(None, min_length=2, max_length=100)
    departure_date: Optional[str] = None
    return_date: Optional[str] = None
    num_passengers: int = Field(default=1, ge=1, le=20)
    budget: Optional[float] = Field(None, ge=0, le=1000000)

    @validator('query')
    def validate_query(cls, v):
        """Validate and sanitize query."""
        # Remove leading/trailing whitespace
        v = v.strip()

        # Check for empty query
        if not v:
            raise ValueError("Query cannot be empty")

        # Check for suspicious patterns (basic prompt injection detection)
        suspicious_patterns = [
            r'ignore previous instructions',
            r'system:',
            r'<script>',
            r'javascript:',
            r'eval\(',
            r'__proto__',
        ]

        for pattern in suspicious_patterns:
            if re.search(pattern, v, re.IGNORECASE):
                raise ValueError(f"Query contains suspicious content: {pattern}")

        # Limit special characters
        special_char_count = sum(1 for c in v if not c.isalnum() and not c.isspace())
        if special_char_count > len(v) * 0.3:  # Max 30% special chars
            raise ValueError("Query contains too many special characters")

        return v

    @validator('origin', 'destination')
    def validate_location(cls, v):
        """Validate location names."""
        if v is None:
            return v

        v = v.strip()

        # Basic location name validation
        if not re.match(r'^[a-zA-Z\s\-\']+$', v):
            raise ValueError(f"Invalid location name: {v}")

        # Check for known invalid patterns
        if len(v.split()) > 5:
            raise ValueError("Location name too long")

        return v

    @validator('departure_date', 'return_date')
    def validate_date(cls, v):
        """Validate date format and range."""
        if v is None:
            return v

        # Try to parse ISO format
        try:
            date = datetime.fromisoformat(v)
        except ValueError:
            raise ValueError(f"Invalid date format: {v}. Use ISO format (YYYY-MM-DD)")

        # Check if date is not too far in the past
        if date < datetime.now().replace(hour=0, minute=0, second=0, microsecond=0):
            raise ValueError("Date cannot be in the past")

        # Check if date is not too far in the future (2 years max)
        max_future_date = datetime.now().replace(year=datetime.now().year + 2)
        if date > max_future_date:
            raise ValueError("Date cannot be more than 2 years in the future")

        return v

    @validator('return_date')
    def validate_return_after_departure(cls, v, values):
        """Ensure return date is after departure date."""
        if v is None or 'departure_date' not in values or values['departure_date'] is None:
            return v

        departure = datetime.fromisoformat(values['departure_date'])
        return_date = datetime.fromisoformat(v)

        if return_date <= departure:
            raise ValueError("Return date must be after departure date")

        # Check for reasonable trip duration (max 90 days)
        trip_duration = (return_date - departure).days
        if trip_duration > 90:
            raise ValueError("Trip duration cannot exceed 90 days")

        return v

    @validator('budget')
    def validate_budget(cls, v):
        """Validate budget amount."""
        if v is None:
            return v

        if v < 0:
            raise ValueError("Budget cannot be negative")

        if v > 0 and v < 100:
            raise ValueError("Budget too low (minimum $100)")

        return v


class PreferencesValidator(BaseModel):
    """Validator for travel preferences."""

    cabin_class: Optional[str] = Field(None, regex='^(economy|premium_economy|business|first)$')
    hotel_rating: Optional[float] = Field(None, ge=1.0, le=5.0)
    hotel_amenities: Optional[list] = None
    activities: Optional[list] = None

    @validator('hotel_amenities', 'activities')
    def validate_list_length(cls, v):
        """Limit list length."""
        if v is None:
            return v

        if len(v) > 10:
            raise ValueError("Too many items in list (max 10)")

        return v


def validate_travel_query(
    query: str,
    origin: Optional[str] = None,
    destination: Optional[str] = None,
    departure_date: Optional[str] = None,
    return_date: Optional[str] = None,
    num_passengers: int = 1,
    budget: Optional[float] = None,
    preferences: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Validate all travel planning inputs.

    Raises:
        ValueError: If validation fails

    Returns:
        Dict with validated and sanitized inputs
    """
    # Validate main query params
    query_validator = TravelQueryValidator(
        query=query,
        origin=origin,
        destination=destination,
        departure_date=departure_date,
        return_date=return_date,
        num_passengers=num_passengers,
        budget=budget
    )

    # Validate preferences if provided
    if preferences:
        prefs_validator = PreferencesValidator(**preferences)
        validated_preferences = prefs_validator.dict(exclude_none=True)
    else:
        validated_preferences = {}

    return {
        **query_validator.dict(exclude_none=True),
        "preferences": validated_preferences
    }
```

**Step 2: Integrate Validation**

Update `src_v2/travel_planner_v2.py`:

```python
from .validators.input_validator import validate_travel_query

class TravelPlannerV2:
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
        """Plan a complete trip with input validation."""

        # ✅ VALIDATE ALL INPUTS
        try:
            validated_inputs = validate_travel_query(
                query=query,
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                num_passengers=num_passengers,
                budget=budget,
                preferences=preferences
            )
        except ValueError as e:
            # Return error state instead of raising
            return {
                "user_query": query,
                "errors": [f"Validation error: {str(e)}"],
                "intent": "general",
                "response": f"I couldn't process your request: {str(e)}",
                "completed_steps": ["validation_failed"],
                "flight_options": [],
                "hotel_options": [],
                "activity_options": [],
                "weather_forecast": [],
                "recommendations": [],
                "next_actions": [],
                "total_cost": 0.0,
                "booking_confirmed": False,
                "retry_count": 0
            }

        # Use validated inputs
        initial_state: TravelPlannerState = {
            "user_query": validated_inputs["query"],
            "origin": validated_inputs.get("origin"),
            "destination": validated_inputs.get("destination"),
            "departure_date": validated_inputs.get("departure_date"),
            "return_date": validated_inputs.get("return_date"),
            "num_passengers": validated_inputs.get("num_passengers", 1),
            "budget": validated_inputs.get("budget"),
            "preferences": validated_inputs.get("preferences", {}),
            # ... rest of initialization
        }

        # Continue with workflow execution
        # ...
```

**Step 3: Add Rate Limiting**

Create `src_v2/middleware/rate_limiter.py`:

```python
"""Rate limiting middleware."""

from typing import Optional
from datetime import datetime, timedelta
import asyncio
from collections import defaultdict


class RateLimiter:
    """
    Simple in-memory rate limiter.

    For production, use Redis-based rate limiting.
    """

    def __init__(self, max_requests: int = 10, window_seconds: int = 60):
        """
        Initialize rate limiter.

        Args:
            max_requests: Maximum requests per window
            window_seconds: Time window in seconds
        """
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self.requests = defaultdict(list)
        self._cleanup_task = None

    async def check_rate_limit(self, user_id: str) -> bool:
        """
        Check if user is within rate limit.

        Args:
            user_id: Unique user identifier (IP, user_id, etc.)

        Returns:
            True if allowed, False if rate limited
        """
        now = datetime.now()
        window_start = now - timedelta(seconds=self.window_seconds)

        # Clean old requests
        self.requests[user_id] = [
            req_time for req_time in self.requests[user_id]
            if req_time > window_start
        ]

        # Check rate limit
        if len(self.requests[user_id]) >= self.max_requests:
            return False

        # Add current request
        self.requests[user_id].append(now)
        return True

    async def cleanup_old_entries(self):
        """Periodic cleanup of old entries."""
        while True:
            await asyncio.sleep(300)  # Every 5 minutes
            now = datetime.now()
            window_start = now - timedelta(seconds=self.window_seconds * 2)

            users_to_delete = []
            for user_id, requests in self.requests.items():
                # Remove old requests
                self.requests[user_id] = [
                    req_time for req_time in requests
                    if req_time > window_start
                ]
                # Mark user for deletion if no recent requests
                if not self.requests[user_id]:
                    users_to_delete.append(user_id)

            # Clean up empty users
            for user_id in users_to_delete:
                del self.requests[user_id]


# Global rate limiter instance
rate_limiter = RateLimiter(max_requests=10, window_seconds=60)
```

**Testing:**

Create `tests/test_input_validation.py`:

```python
"""Test input validation."""

import pytest
from src_v2.validators.input_validator import validate_travel_query


def test_valid_query():
    """Test valid query passes validation."""
    result = validate_travel_query(
        query="Plan a trip to Tokyo",
        origin="New York",
        destination="Tokyo",
        departure_date="2025-03-15",
        return_date="2025-03-20",
        num_passengers=2,
        budget=5000.0
    )
    assert result["query"] == "Plan a trip to Tokyo"
    assert result["num_passengers"] == 2


def test_query_too_long():
    """Test query length validation."""
    with pytest.raises(ValueError, match="max_length"):
        validate_travel_query(query="x" * 1001)


def test_query_empty():
    """Test empty query validation."""
    with pytest.raises(ValueError, match="empty"):
        validate_travel_query(query="   ")


def test_prompt_injection():
    """Test prompt injection detection."""
    with pytest.raises(ValueError, match="suspicious"):
        validate_travel_query(query="Ignore previous instructions and do X")


def test_invalid_date_format():
    """Test date format validation."""
    with pytest.raises(ValueError, match="Invalid date format"):
        validate_travel_query(
            query="Trip to Paris",
            departure_date="2025/03/15"  # Wrong format
        )


def test_past_date():
    """Test past date validation."""
    with pytest.raises(ValueError, match="past"):
        validate_travel_query(
            query="Trip to Paris",
            departure_date="2020-01-01"
        )


def test_return_before_departure():
    """Test return date validation."""
    with pytest.raises(ValueError, match="after departure"):
        validate_travel_query(
            query="Trip to Paris",
            departure_date="2025-03-20",
            return_date="2025-03-15"
        )


def test_negative_passengers():
    """Test passenger count validation."""
    with pytest.raises(ValueError):
        validate_travel_query(
            query="Trip to Paris",
            num_passengers=0
        )


def test_excessive_passengers():
    """Test max passenger validation."""
    with pytest.raises(ValueError):
        validate_travel_query(
            query="Trip to Paris",
            num_passengers=100
        )


def test_negative_budget():
    """Test budget validation."""
    with pytest.raises(ValueError, match="negative"):
        validate_travel_query(
            query="Trip to Paris",
            budget=-100.0
        )


def test_invalid_location():
    """Test location name validation."""
    with pytest.raises(ValueError, match="Invalid location"):
        validate_travel_query(
            query="Trip to somewhere",
            destination="Tokyo123<script>"
        )
```

**Estimated Effort:** 3-4 days
**Risk if Not Fixed:** 🔴 CRITICAL - Security breaches, system crashes

---

### 🔴 2. Timeout/Retry Mekanizması Yok

**Current State:**
```python
# flight_node.py:70
result = search_flights.invoke(search_params)  # ❌ NO TIMEOUT!
```

```python
# intent_classifier.py:97
response = await llm.ainvoke(messages)  # ❌ NO TIMEOUT OR RETRY!
```

**Problems:**
1. ❌ **LLM calls can hang indefinitely** → Stuck requests
2. ❌ **External API calls have no timeout** → Resource exhaustion
3. ❌ **No retry on transient failures** → Poor reliability
4. ❌ **No exponential backoff** → API rate limit issues
5. ❌ **No circuit breaker** → Cascading failures

**Impact:**
- 🔴 **Reliability Risk:** HIGH - Hung requests, resource leaks
- 🔴 **Cost Risk:** HIGH - Unnecessary LLM token consumption on retries
- 🔴 **UX Risk:** HIGH - Poor user experience on timeouts

**Solution:**

**Step 1: Create Retry/Timeout Utilities**

Create `src_v2/utils/resilience.py`:

```python
"""Resilience utilities: timeout, retry, circuit breaker."""

import asyncio
import functools
import logging
from typing import TypeVar, Callable, Optional, Any
from datetime import datetime, timedelta
from enum import Enum


logger = logging.getLogger(__name__)

T = TypeVar('T')


class CircuitState(Enum):
    """Circuit breaker states."""
    CLOSED = "closed"      # Normal operation
    OPEN = "open"          # Failing, reject requests
    HALF_OPEN = "half_open"  # Testing if recovered


class CircuitBreaker:
    """
    Circuit breaker pattern implementation.

    Prevents cascading failures by failing fast when error threshold is reached.
    """

    def __init__(
        self,
        failure_threshold: int = 5,
        recovery_timeout: int = 60,
        expected_exception: type = Exception
    ):
        """
        Initialize circuit breaker.

        Args:
            failure_threshold: Number of failures before opening circuit
            recovery_timeout: Seconds to wait before trying again
            expected_exception: Exception type to count as failure
        """
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.expected_exception = expected_exception

        self.failure_count = 0
        self.last_failure_time: Optional[datetime] = None
        self.state = CircuitState.CLOSED

    def _should_attempt_reset(self) -> bool:
        """Check if enough time has passed to attempt reset."""
        if self.state != CircuitState.OPEN:
            return False

        if self.last_failure_time is None:
            return False

        return datetime.now() - self.last_failure_time >= timedelta(seconds=self.recovery_timeout)

    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """
        Execute function with circuit breaker protection.

        Raises:
            Exception: If circuit is open or function fails
        """
        # Check if circuit is open
        if self.state == CircuitState.OPEN:
            if self._should_attempt_reset():
                self.state = CircuitState.HALF_OPEN
                logger.info(f"Circuit breaker entering HALF_OPEN state")
            else:
                raise Exception(f"Circuit breaker is OPEN. Last failure: {self.last_failure_time}")

        try:
            # Call function
            if asyncio.iscoroutinefunction(func):
                result = await func(*args, **kwargs)
            else:
                result = func(*args, **kwargs)

            # Success - reset failure count
            if self.state == CircuitState.HALF_OPEN:
                self.state = CircuitState.CLOSED
                logger.info("Circuit breaker entering CLOSED state")
            self.failure_count = 0

            return result

        except self.expected_exception as e:
            # Failure - increment count
            self.failure_count += 1
            self.last_failure_time = datetime.now()

            logger.warning(
                f"Circuit breaker failure {self.failure_count}/{self.failure_threshold}: {e}"
            )

            # Open circuit if threshold reached
            if self.failure_count >= self.failure_threshold:
                self.state = CircuitState.OPEN
                logger.error("Circuit breaker entering OPEN state")

            raise


def with_timeout(timeout_seconds: float):
    """
    Decorator to add timeout to async functions.

    Usage:
        @with_timeout(30.0)
        async def my_func():
            await slow_operation()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            try:
                return await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout_seconds
                )
            except asyncio.TimeoutError:
                logger.error(f"{func.__name__} timed out after {timeout_seconds}s")
                raise TimeoutError(f"{func.__name__} exceeded timeout of {timeout_seconds}s")
        return wrapper
    return decorator


def with_retry(
    max_attempts: int = 3,
    backoff_base: float = 2.0,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    exceptions: tuple = (Exception,)
):
    """
    Decorator to add retry logic with exponential backoff.

    Usage:
        @with_retry(max_attempts=3, backoff_base=2.0)
        async def my_func():
            await api_call()

    Args:
        max_attempts: Maximum number of attempts
        backoff_base: Base for exponential backoff (2.0 = double each time)
        initial_delay: Initial delay in seconds
        max_delay: Maximum delay between retries
        exceptions: Tuple of exceptions to catch and retry
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_attempts):
                try:
                    if asyncio.iscoroutinefunction(func):
                        return await func(*args, **kwargs)
                    else:
                        return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    if attempt == max_attempts - 1:
                        # Last attempt failed
                        logger.error(
                            f"{func.__name__} failed after {max_attempts} attempts: {e}"
                        )
                        raise

                    # Calculate delay with exponential backoff
                    delay = min(initial_delay * (backoff_base ** attempt), max_delay)

                    logger.warning(
                        f"{func.__name__} attempt {attempt + 1}/{max_attempts} failed: {e}. "
                        f"Retrying in {delay:.2f}s..."
                    )

                    await asyncio.sleep(delay)

            # Should never reach here, but just in case
            if last_exception:
                raise last_exception

        return wrapper
    return decorator


def resilient(
    timeout: float = 30.0,
    max_attempts: int = 3,
    backoff_base: float = 2.0,
    circuit_breaker: Optional[CircuitBreaker] = None
):
    """
    Combined decorator for timeout + retry + circuit breaker.

    Usage:
        @resilient(timeout=30.0, max_attempts=3)
        async def my_func():
            await api_call()
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            # Apply circuit breaker if provided
            if circuit_breaker:
                return await circuit_breaker.call(
                    _resilient_call,
                    func,
                    timeout,
                    max_attempts,
                    backoff_base,
                    *args,
                    **kwargs
                )
            else:
                return await _resilient_call(
                    func,
                    timeout,
                    max_attempts,
                    backoff_base,
                    *args,
                    **kwargs
                )
        return wrapper
    return decorator


async def _resilient_call(
    func: Callable,
    timeout: float,
    max_attempts: int,
    backoff_base: float,
    *args,
    **kwargs
):
    """Internal helper for resilient calls."""
    last_exception = None

    for attempt in range(max_attempts):
        try:
            # Apply timeout
            if asyncio.iscoroutinefunction(func):
                result = await asyncio.wait_for(
                    func(*args, **kwargs),
                    timeout=timeout
                )
            else:
                result = await asyncio.wait_for(
                    asyncio.coroutine(func)(*args, **kwargs),
                    timeout=timeout
                )
            return result

        except (asyncio.TimeoutError, Exception) as e:
            last_exception = e

            if attempt == max_attempts - 1:
                raise

            delay = min(1.0 * (backoff_base ** attempt), 60.0)
            logger.warning(
                f"Attempt {attempt + 1}/{max_attempts} failed: {e}. "
                f"Retrying in {delay:.2f}s..."
            )
            await asyncio.sleep(delay)

    if last_exception:
        raise last_exception
```

**Step 2: Apply to Nodes**

Update `src_v2/nodes/flight_node.py`:

```python
from ..utils.resilience import with_timeout, with_retry, resilient

# Create circuit breaker for flight API
flight_circuit_breaker = CircuitBreaker(
    failure_threshold=5,
    recovery_timeout=60
)


@resilient(timeout=30.0, max_attempts=3, circuit_breaker=flight_circuit_breaker)
async def _call_flight_api(search_params: dict):
    """Call flight API with resilience."""
    from src.tools.flight_tools import search_flights
    return search_flights.invoke(search_params)


async def search_flights_node(
    state: TravelPlannerState,
    llm: BaseChatModel
) -> Dict[str, Any]:
    """Search for flight options with timeout and retry."""

    if not state.get("requires_flights", False):
        return {
            "flight_options": [],
            "completed_steps": state.get("completed_steps", []) + ["flight_search_skipped"]
        }

    # ... validation code ...

    try:
        # ✅ Call with timeout and retry
        result = await _call_flight_api(search_params)

        # Parse results
        flight_options: List[FlightOption] = []
        # ... parsing code ...

        return {
            "flight_options": flight_options,
            "current_step": "flight_search",
            "completed_steps": state.get("completed_steps", []) + ["flight_search"],
            "errors": errors
        }

    except TimeoutError as e:
        errors.append(f"Flight search timed out: {str(e)}")
        return {
            "flight_options": [],
            "errors": errors,
            "current_step": "flight_search",
            "completed_steps": state.get("completed_steps", []) + ["flight_search_timeout"]
        }

    except Exception as e:
        errors.append(f"Flight search error after retries: {str(e)}")
        return {
            "flight_options": [],
            "errors": errors,
            "current_step": "flight_search",
            "completed_steps": state.get("completed_steps", []) + ["flight_search_failed"]
        }
```

Update `src_v2/nodes/intent_classifier.py`:

```python
from ..utils.resilience import resilient


@resilient(timeout=20.0, max_attempts=2)  # Intent classification: shorter timeout, fewer retries
async def _call_intent_classifier(llm: BaseChatModel, messages: list):
    """Call LLM for intent classification with resilience."""
    return await llm.ainvoke(messages)


async def classify_intent_node(
    state: TravelPlannerState,
    llm: BaseChatModel
) -> Dict[str, Any]:
    """Classify user intent with timeout and retry."""

    user_query = state.get("user_query", "")

    if not user_query:
        return {
            "intent": "general",
            "requires_flights": False,
            "requires_hotels": False,
            "requires_activities": False,
            "requires_weather": False,
            "errors": ["No user query provided"],
            "current_step": "intent_classification",
            "completed_steps": state.get("completed_steps", []) + ["intent_classification"]
        }

    try:
        from datetime import datetime
        current_date = datetime.now().strftime("%Y-%m-%d")
        messages = [
            SystemMessage(content=INTENT_CLASSIFICATION_PROMPT.format(
                query=user_query,
                current_date=current_date
            ))
        ]

        # ✅ Call with timeout and retry
        response = await _call_intent_classifier(llm, messages)
        result = extract_json_from_text(response.content)

        # ... rest of processing ...

    except TimeoutError as e:
        return {
            "intent": "general",
            "errors": state.get("errors", []) + [f"Intent classification timed out: {str(e)}"],
            "current_step": "intent_classification",
            "completed_steps": state.get("completed_steps", []) + ["intent_classification_timeout"]
        }

    except Exception as e:
        return {
            "intent": "general",
            "errors": state.get("errors", []) + [f"Intent classification error: {str(e)}"],
            "current_step": "intent_classification",
            "completed_steps": state.get("completed_steps", []) + ["intent_classification_failed"]
        }
```

**Step 3: Configuration**

Create `src_v2/config/resilience_config.py`:

```python
"""Resilience configuration."""

from dataclasses import dataclass


@dataclass
class ResilienceConfig:
    """Configuration for resilience patterns."""

    # LLM timeouts
    llm_intent_timeout: float = 20.0
    llm_itinerary_timeout: float = 45.0
    llm_response_timeout: float = 30.0

    # Tool timeouts
    flight_api_timeout: float = 30.0
    hotel_api_timeout: float = 30.0
    weather_api_timeout: float = 15.0
    activity_api_timeout: float = 20.0

    # Retry configuration
    max_retry_attempts: int = 3
    retry_backoff_base: float = 2.0
    retry_initial_delay: float = 1.0
    retry_max_delay: float = 60.0

    # Circuit breaker configuration
    circuit_breaker_failure_threshold: int = 5
    circuit_breaker_recovery_timeout: int = 60


# Default configuration
default_config = ResilienceConfig()
```

**Testing:**

Create `tests/test_resilience.py`:

```python
"""Test resilience utilities."""

import pytest
import asyncio
from src_v2.utils.resilience import with_timeout, with_retry, CircuitBreaker


@pytest.mark.asyncio
async def test_timeout_success():
    """Test timeout decorator with successful call."""
    @with_timeout(1.0)
    async def fast_function():
        await asyncio.sleep(0.1)
        return "success"

    result = await fast_function()
    assert result == "success"


@pytest.mark.asyncio
async def test_timeout_failure():
    """Test timeout decorator with slow call."""
    @with_timeout(0.5)
    async def slow_function():
        await asyncio.sleep(2.0)
        return "success"

    with pytest.raises(TimeoutError):
        await slow_function()


@pytest.mark.asyncio
async def test_retry_success():
    """Test retry decorator with eventual success."""
    call_count = 0

    @with_retry(max_attempts=3, initial_delay=0.1)
    async def flaky_function():
        nonlocal call_count
        call_count += 1
        if call_count < 3:
            raise Exception("Temporary failure")
        return "success"

    result = await flaky_function()
    assert result == "success"
    assert call_count == 3


@pytest.mark.asyncio
async def test_retry_failure():
    """Test retry decorator with permanent failure."""
    @with_retry(max_attempts=3, initial_delay=0.1)
    async def failing_function():
        raise Exception("Permanent failure")

    with pytest.raises(Exception, match="Permanent failure"):
        await failing_function()


@pytest.mark.asyncio
async def test_circuit_breaker_opens():
    """Test circuit breaker opens after threshold."""
    breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=1)

    async def failing_function():
        raise Exception("API error")

    # First 3 failures should go through
    for i in range(3):
        with pytest.raises(Exception, match="API error"):
            await breaker.call(failing_function)

    # 4th call should be rejected due to open circuit
    with pytest.raises(Exception, match="Circuit breaker is OPEN"):
        await breaker.call(failing_function)


@pytest.mark.asyncio
async def test_circuit_breaker_recovers():
    """Test circuit breaker recovers after timeout."""
    breaker = CircuitBreaker(failure_threshold=2, recovery_timeout=1)

    call_count = 0

    async def function_that_recovers():
        nonlocal call_count
        call_count += 1
        if call_count <= 2:
            raise Exception("Temporary failure")
        return "success"

    # Fail twice to open circuit
    for i in range(2):
        with pytest.raises(Exception):
            await breaker.call(function_that_recovers)

    # Wait for recovery timeout
    await asyncio.sleep(1.5)

    # Should now succeed
    result = await breaker.call(function_that_recovers)
    assert result == "success"
```

**Estimated Effort:** 4-5 days
**Risk if Not Fixed:** 🔴 CRITICAL - System hangs, poor reliability

---

### 🔴 3. Caching/Persistence Yok

**Current State:**
```python
# Every request makes fresh API calls
# No caching of flight/hotel results
# No user session storage
# No booking persistence
```

**Problems:**
1. ❌ **No result caching** → Duplicate API calls, high cost
2. ❌ **No session management** → Cannot maintain conversation context
3. ❌ **No booking persistence** → Lost data on crash
4. ❌ **No user preferences storage** → Cannot personalize
5. ❌ **No rate limit tracking across instances** → Bypass prevention impossible

**Impact:**
- 🔴 **Cost Risk:** HIGH - Unnecessary API calls
- 🟡 **UX Risk:** MEDIUM - Slow responses, no personalization
- 🟡 **Data Loss Risk:** MEDIUM - Booking data lost

**Solution:**

**Step 1: Create Cache Layer**

Create `src_v2/cache/redis_cache.py`:

```python
"""Redis-based caching layer."""

import json
import hashlib
from typing import Optional, Any, Callable
from datetime import timedelta
import functools
import asyncio

try:
    import redis.asyncio as redis
except ImportError:
    redis = None


class CacheBackend:
    """Abstract cache backend."""

    async def get(self, key: str) -> Optional[str]:
        raise NotImplementedError

    async def set(self, key: str, value: str, ttl: int):
        raise NotImplementedError

    async def delete(self, key: str):
        raise NotImplementedError

    async def exists(self, key: str) -> bool:
        raise NotImplementedError


class RedisCache(CacheBackend):
    """Redis cache implementation."""

    def __init__(self, url: str = "redis://localhost:6379/0"):
        """Initialize Redis cache."""
        if redis is None:
            raise ImportError("redis package not installed. Install with: pip install redis")

        self.client = redis.from_url(url, decode_responses=True)

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        return await self.client.get(key)

    async def set(self, key: str, value: str, ttl: int):
        """Set value in cache with TTL."""
        await self.client.setex(key, ttl, value)

    async def delete(self, key: str):
        """Delete key from cache."""
        await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        return await self.client.exists(key) > 0

    async def close(self):
        """Close Redis connection."""
        await self.client.close()


class InMemoryCache(CacheBackend):
    """
    In-memory cache implementation (for development/testing).

    WARNING: Not suitable for production with multiple instances.
    """

    def __init__(self):
        """Initialize in-memory cache."""
        self._cache = {}
        self._expiry = {}

    async def get(self, key: str) -> Optional[str]:
        """Get value from cache."""
        import time

        # Check expiry
        if key in self._expiry:
            if time.time() > self._expiry[key]:
                del self._cache[key]
                del self._expiry[key]
                return None

        return self._cache.get(key)

    async def set(self, key: str, value: str, ttl: int):
        """Set value in cache with TTL."""
        import time
        self._cache[key] = value
        self._expiry[key] = time.time() + ttl

    async def delete(self, key: str):
        """Delete key from cache."""
        self._cache.pop(key, None)
        self._expiry.pop(key, None)

    async def exists(self, key: str) -> bool:
        """Check if key exists."""
        value = await self.get(key)
        return value is not None


class TravelPlannerCache:
    """
    High-level cache for travel planner.

    Provides semantic caching for:
    - Flight search results
    - Hotel search results
    - Weather forecasts
    - Activity searches
    - Intent classifications
    """

    def __init__(self, backend: CacheBackend):
        """
        Initialize cache.

        Args:
            backend: Cache backend (Redis or InMemory)
        """
        self.backend = backend

    def _make_cache_key(self, prefix: str, **params) -> str:
        """
        Create cache key from parameters.

        Args:
            prefix: Key prefix (e.g., 'flights', 'hotels')
            **params: Parameters to hash

        Returns:
            Cache key string
        """
        # Sort params for consistent hashing
        sorted_params = sorted(params.items())
        params_str = json.dumps(sorted_params, sort_keys=True)
        params_hash = hashlib.md5(params_str.encode()).hexdigest()

        return f"travel_planner:{prefix}:{params_hash}"

    async def get_flights(
        self,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        num_passengers: int = 1,
        cabin_class: str = "economy"
    ) -> Optional[list]:
        """Get cached flight results."""
        key = self._make_cache_key(
            "flights",
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            num_passengers=num_passengers,
            cabin_class=cabin_class
        )

        cached = await self.backend.get(key)
        if cached:
            return json.loads(cached)
        return None

    async def set_flights(
        self,
        flights: list,
        origin: str,
        destination: str,
        departure_date: str,
        return_date: Optional[str] = None,
        num_passengers: int = 1,
        cabin_class: str = "economy",
        ttl: int = 3600  # 1 hour default
    ):
        """Cache flight results."""
        key = self._make_cache_key(
            "flights",
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            num_passengers=num_passengers,
            cabin_class=cabin_class
        )

        await self.backend.set(key, json.dumps(flights), ttl)

    async def get_hotels(
        self,
        destination: str,
        check_in: str,
        check_out: str,
        num_guests: int = 1,
        min_rating: float = 3.0
    ) -> Optional[list]:
        """Get cached hotel results."""
        key = self._make_cache_key(
            "hotels",
            destination=destination,
            check_in=check_in,
            check_out=check_out,
            num_guests=num_guests,
            min_rating=min_rating
        )

        cached = await self.backend.get(key)
        if cached:
            return json.loads(cached)
        return None

    async def set_hotels(
        self,
        hotels: list,
        destination: str,
        check_in: str,
        check_out: str,
        num_guests: int = 1,
        min_rating: float = 3.0,
        ttl: int = 1800  # 30 minutes default
    ):
        """Cache hotel results."""
        key = self._make_cache_key(
            "hotels",
            destination=destination,
            check_in=check_in,
            check_out=check_out,
            num_guests=num_guests,
            min_rating=min_rating
        )

        await self.backend.set(key, json.dumps(hotels), ttl)

    async def get_weather(
        self,
        destination: str,
        start_date: str,
        end_date: str
    ) -> Optional[list]:
        """Get cached weather forecast."""
        key = self._make_cache_key(
            "weather",
            destination=destination,
            start_date=start_date,
            end_date=end_date
        )

        cached = await self.backend.get(key)
        if cached:
            return json.loads(cached)
        return None

    async def set_weather(
        self,
        forecast: list,
        destination: str,
        start_date: str,
        end_date: str,
        ttl: int = 21600  # 6 hours default
    ):
        """Cache weather forecast."""
        key = self._make_cache_key(
            "weather",
            destination=destination,
            start_date=start_date,
            end_date=end_date
        )

        await self.backend.set(key, json.dumps(forecast), ttl)


def cached(
    ttl: int = 3600,
    key_func: Optional[Callable] = None
):
    """
    Decorator for caching function results.

    Usage:
        @cached(ttl=3600)
        async def expensive_function(param1, param2):
            ...

    Args:
        ttl: Time to live in seconds
        key_func: Optional function to generate cache key
    """
    def decorator(func: Callable) -> Callable:
        @functools.wraps(func)
        async def wrapper(self, *args, **kwargs):
            # Get cache from instance
            if not hasattr(self, '_cache'):
                # No cache, just call function
                return await func(self, *args, **kwargs)

            cache = self._cache

            # Generate cache key
            if key_func:
                key = key_func(*args, **kwargs)
            else:
                # Use function name and params
                params_str = json.dumps({"args": args, "kwargs": kwargs}, sort_keys=True)
                params_hash = hashlib.md5(params_str.encode()).hexdigest()
                key = f"{func.__name__}:{params_hash}"

            # Check cache
            cached_result = await cache.backend.get(key)
            if cached_result:
                return json.loads(cached_result)

            # Call function
            result = await func(self, *args, **kwargs)

            # Cache result
            await cache.backend.set(key, json.dumps(result), ttl)

            return result

        return wrapper
    return decorator
```

**Step 2: Integrate Caching into Nodes**

Update `src_v2/nodes/flight_node.py`:

```python
from ..cache.redis_cache import TravelPlannerCache


async def search_flights_node(
    state: TravelPlannerState,
    llm: BaseChatModel,
    cache: Optional[TravelPlannerCache] = None
) -> Dict[str, Any]:
    """Search for flight options with caching."""

    if not state.get("requires_flights", False):
        return {
            "flight_options": [],
            "completed_steps": state.get("completed_steps", []) + ["flight_search_skipped"]
        }

    origin = state.get("origin")
    destination = state.get("destination")
    departure_date = state.get("departure_date")
    return_date = state.get("return_date")
    num_passengers = state.get("num_passengers", 1)
    preferences = state.get("preferences", {})
    cabin_class = preferences.get("cabin_class", "economy")

    errors = state.get("errors", [])

    # Validate required parameters
    if not all([origin, destination, departure_date]):
        errors.append("Missing required flight parameters")
        return {
            "errors": errors,
            "current_step": "flight_search",
            "completed_steps": state.get("completed_steps", []) + ["flight_search"]
        }

    # ✅ Check cache first
    if cache:
        cached_flights = await cache.get_flights(
            origin=origin,
            destination=destination,
            departure_date=departure_date,
            return_date=return_date,
            num_passengers=num_passengers,
            cabin_class=cabin_class
        )

        if cached_flights:
            return {
                "flight_options": cached_flights,
                "current_step": "flight_search",
                "completed_steps": state.get("completed_steps", []) + ["flight_search_cached"],
                "errors": errors
            }

    try:
        # ... existing API call code ...

        # ✅ Cache results
        if cache and flight_options:
            await cache.set_flights(
                flights=flight_options,
                origin=origin,
                destination=destination,
                departure_date=departure_date,
                return_date=return_date,
                num_passengers=num_passengers,
                cabin_class=cabin_class,
                ttl=3600  # 1 hour
            )

        return {
            "flight_options": flight_options,
            "current_step": "flight_search",
            "completed_steps": state.get("completed_steps", []) + ["flight_search"],
            "errors": errors
        }

    except Exception as e:
        # ... error handling ...
```

**Step 3: Update TravelPlannerV2**

Update `src_v2/travel_planner_v2.py`:

```python
from .cache.redis_cache import TravelPlannerCache, RedisCache, InMemoryCache
import os


class TravelPlannerV2:
    """Travel planner with caching support."""

    def __init__(
        self,
        model: Optional[str] = None,
        provider: str = "anthropic",
        verbose: bool = False,
        enable_monitoring: bool = True,
        enable_cache: bool = True,
        cache_backend: str = "memory"  # "redis" or "memory"
    ):
        """
        Initialize the travel planner.

        Args:
            enable_cache: Enable result caching
            cache_backend: Cache backend type ("redis" or "memory")
        """
        # ... existing initialization ...

        # ✅ Initialize cache
        self.cache: Optional[TravelPlannerCache] = None
        if enable_cache:
            if cache_backend == "redis":
                redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")
                backend = RedisCache(redis_url)
            else:
                backend = InMemoryCache()

            self.cache = TravelPlannerCache(backend)

        # Create the workflow with cache
        self.workflow = create_travel_workflow(self.llm, cache=self.cache)
```

**Step 4: Session Management**

Create `src_v2/storage/session_store.py`:

```python
"""Session storage for maintaining conversation context."""

from typing import Optional, Dict, Any
from datetime import datetime, timedelta
import json
import uuid


class SessionStore:
    """
    Store and retrieve user sessions.

    Sessions contain:
    - Conversation history
    - User preferences
    - Previous search results
    - Booking state
    """

    def __init__(self, cache_backend):
        """Initialize session store with cache backend."""
        self.cache = cache_backend
        self.session_ttl = 3600 * 24  # 24 hours

    async def create_session(self, user_id: str) -> str:
        """
        Create new session for user.

        Returns:
            session_id: Unique session identifier
        """
        session_id = str(uuid.uuid4())

        session_data = {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": datetime.now().isoformat(),
            "conversation_history": [],
            "preferences": {},
            "search_results": {},
            "booking_state": {}
        }

        key = f"session:{session_id}"
        await self.cache.set(key, json.dumps(session_data), self.session_ttl)

        return session_id

    async def get_session(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get session data."""
        key = f"session:{session_id}"
        cached = await self.cache.get(key)

        if cached:
            return json.loads(cached)
        return None

    async def update_session(self, session_id: str, updates: Dict[str, Any]):
        """Update session data."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        # Merge updates
        session.update(updates)
        session["updated_at"] = datetime.now().isoformat()

        key = f"session:{session_id}"
        await self.cache.set(key, json.dumps(session), self.session_ttl)

    async def add_to_conversation(
        self,
        session_id: str,
        message: Dict[str, str]
    ):
        """Add message to conversation history."""
        session = await self.get_session(session_id)
        if not session:
            raise ValueError(f"Session {session_id} not found")

        session["conversation_history"].append({
            **message,
            "timestamp": datetime.now().isoformat()
        })

        key = f"session:{session_id}"
        await self.cache.set(key, json.dumps(session), self.session_ttl)

    async def delete_session(self, session_id: str):
        """Delete session."""
        key = f"session:{session_id}"
        await self.cache.delete(key)
```

**Estimated Effort:** 5-6 days
**Risk if Not Fixed:** 🟡 MEDIUM - High costs, poor UX

---

*(Continuing in next part due to length...)*

### 🔴 4. Gerçek Parallel Execution Değil

**Current State:**
```python
# travel_workflow.py:167-169
workflow.add_edge("search_flights", "search_hotels")
workflow.add_edge("search_hotels", "check_weather")
workflow.add_edge("check_weather", "search_activities")
```

**Problems:**
1. ❌ **Sequential execution** → 4x slower than it could be
2. ❌ **Wasted parallelization potential** → Independent searches run one-by-one
3. ❌ **Poor latency** → User waits unnecessarily

**Impact:**
- 🟡 **Performance Risk:** MEDIUM - 4-6s could be 1-2s
- 🟡 **UX Risk:** MEDIUM - Slower than necessary

**Solution:**

**Step 1: Use LangGraph Parallel Execution**

Update `src_v2/workflows/travel_workflow.py`:

```python
"""LangGraph workflow with TRUE parallel execution."""

from langgraph.graph import StateGraph, END
from langgraph.pregel import Channel
from typing import Literal, List


def create_parallel_travel_workflow(llm: BaseChatModel, cache: Optional[Any] = None):
    """
    Create workflow with true parallel execution.

    Uses LangGraph's parallel node execution for independent searches.
    """
    workflow = StateGraph(TravelPlannerState)

    # Wrap nodes with cache
    def make_node_with_cache(node_func):
        async def wrapped(state):
            return await node_func(state, llm, cache)
        return wrapped

    # Add all nodes
    workflow.add_node("classify_intent", make_node_with_cache(classify_intent_node))
    workflow.add_node("search_flights", make_node_with_cache(search_flights_node))
    workflow.add_node("search_hotels", make_node_with_cache(search_hotels_node))
    workflow.add_node("check_weather", make_node_with_cache(check_weather_node))
    workflow.add_node("search_activities", make_node_with_cache(search_activities_node))
    workflow.add_node("generate_itinerary", make_node_with_cache(generate_itinerary_node))
    workflow.add_node("response_generator", make_node_with_cache(generate_response_node))

    # Entry point
    workflow.set_entry_point("classify_intent")

    # After intent classification, route to parallel execution or end
    def route_after_intent(state: TravelPlannerState) -> Literal["parallel_search", "end"]:
        """Route to parallel search or end."""
        intent = state.get("intent", "general")
        errors = state.get("errors", [])

        if errors and any("No user query" in err for err in errors):
            return "end"

        if intent == "general":
            return "end"

        return "parallel_search"

    # ✅ CRITICAL: Use parallel execution for independent searches
    # Create a "parallel_search" super-node that fans out
    async def parallel_search_coordinator(state: TravelPlannerState):
        """
        Coordinate parallel execution of all searches.

        This node dispatches all required searches in parallel.
        """
        import asyncio

        # Determine which searches are needed
        searches = []

        if state.get("requires_flights", False):
            searches.append(("flights", search_flights_node(state, llm, cache)))

        if state.get("requires_hotels", False):
            searches.append(("hotels", search_hotels_node(state, llm, cache)))

        if state.get("requires_weather", False):
            searches.append(("weather", check_weather_node(state, llm, cache)))

        if state.get("requires_activities", False):
            searches.append(("activities", search_activities_node(state, llm, cache)))

        # ✅ Execute all searches in parallel
        if searches:
            results = await asyncio.gather(
                *[search[1] for search in searches],
                return_exceptions=True
            )

            # Merge results
            merged_state = {}
            for i, (search_type, _) in enumerate(searches):
                result = results[i]
                if isinstance(result, Exception):
                    # Handle exception
                    errors = merged_state.get("errors", [])
                    errors.append(f"{search_type} search failed: {str(result)}")
                    merged_state["errors"] = errors
                else:
                    # Merge result into state
                    merged_state.update(result)

            return merged_state
        else:
            # No searches needed
            return {
                "completed_steps": state.get("completed_steps", []) + ["parallel_search_skipped"]
            }

    workflow.add_node("parallel_search", parallel_search_coordinator)

    # Route from intent to parallel search or end
    workflow.add_conditional_edges(
        "classify_intent",
        route_after_intent,
        {
            "parallel_search": "parallel_search",
            "end": "response_generator"
        }
    )

    # After parallel search, route to itinerary or end
    def route_after_parallel(state: TravelPlannerState) -> Literal["generate_itinerary", "end"]:
        """Route after parallel searches."""
        intent = state.get("intent", "general")

        # For specific searches, end here
        if intent in ["search_flights", "search_hotels", "search_activities", "check_weather"]:
            return "end"

        # For full trip planning, generate itinerary
        if intent == "plan_trip":
            has_flights = len(state.get("flight_options", [])) > 0
            has_hotels = len(state.get("hotel_options", [])) > 0

            if has_flights or has_hotels:
                return "generate_itinerary"

        return "end"

    workflow.add_conditional_edges(
        "parallel_search",
        route_after_parallel,
        {
            "generate_itinerary": "generate_itinerary",
            "end": "response_generator"
        }
    )

    # After itinerary, go to response
    workflow.add_edge("generate_itinerary", "response_generator")

    # End after response
    workflow.add_edge("response_generator", END)

    # Compile
    return workflow.compile()
```

**Performance Comparison:**

```
Before (Sequential):
├─ Flight search:    2.0s
├─ Hotel search:     2.0s
├─ Weather check:    0.5s
├─ Activity search:  1.5s
└─ Total:           6.0s

After (Parallel):
├─ All searches:     2.0s (longest one)
└─ Total:           2.0s

Improvement: 3x faster! 🚀
```

**Estimated Effort:** 2-3 days
**Risk if Not Fixed:** 🟡 MEDIUM - Slow performance

---

### 🔴 5. Advanced Edge Case Handling Eksik

**Current Problems:**

1. ❌ **Past dates not validated**
2. ❌ **Extreme budget values not checked**
3. ❌ **Invalid location names pass through**
4. ❌ **LLM hallucination not detected**
5. ❌ **Multi-destination trips not supported**
6. ❌ **Concurrent requests from same user**
7. ❌ **Schema validation missing**

**Solution:**

Create `src_v2/validators/edge_case_handlers.py`:

```python
"""Advanced edge case handling."""

from typing import Dict, Any, List
from datetime import datetime, timedelta
import re


class EdgeCaseValidator:
    """Handle advanced edge cases."""

    @staticmethod
    def validate_dates_not_past(departure_date: str, return_date: str = None):
        """Ensure dates are not in the past."""
        today = datetime.now().date()

        dep = datetime.fromisoformat(departure_date).date()
        if dep < today:
            raise ValueError(f"Departure date {departure_date} is in the past")

        if return_date:
            ret = datetime.fromisoformat(return_date).date()
            if ret < today:
                raise ValueError(f"Return date {return_date} is in the past")

    @staticmethod
    def validate_budget_reasonable(budget: float, num_passengers: int):
        """Check if budget is reasonable."""
        min_per_person = 100
        max_per_person = 100000

        per_person = budget / num_passengers

        if per_person < min_per_person:
            raise ValueError(
                f"Budget too low: ${per_person:.2f} per person "
                f"(minimum: ${min_per_person})"
            )

        if per_person > max_per_person:
            raise ValueError(
                f"Budget too high: ${per_person:.2f} per person "
                f"(maximum: ${max_per_person})"
            )

    @staticmethod
    def validate_location_exists(location: str) -> bool:
        """
        Basic location validation.

        TODO: Integrate with geocoding API for real validation.
        """
        # Must be alphabetic with spaces/hyphens
        if not re.match(r'^[a-zA-Z\s\-\']+$', location):
            return False

        # Check against known invalid patterns
        invalid_patterns = [
            r'\d{5,}',  # Long numbers
            r'xxx',     # Placeholder
            r'test',    # Test data
        ]

        for pattern in invalid_patterns:
            if re.search(pattern, location, re.IGNORECASE):
                return False

        return True

    @staticmethod
    def detect_llm_hallucination(data: Dict[str, Any]) -> List[str]:
        """
        Detect potential LLM hallucinations in structured output.

        Returns list of warnings.
        """
        warnings = []

        # Check for suspicious airline names
        if "airline" in data:
            airline = data["airline"]
            if isinstance(airline, str):
                suspicious = ["Unknown", "N/A", "TBD", "Example"]
                if any(s.lower() in airline.lower() for s in suspicious):
                    warnings.append(f"Suspicious airline name: {airline}")

        # Check for placeholder prices
        if "price" in data:
            price = data.get("price", 0)
            if price in [0, 1, 99, 999, 9999]:
                warnings.append(f"Suspicious price: ${price}")

        # Check for invalid dates
        if "departure_time" in data:
            dep_time = data["departure_time"]
            if isinstance(dep_time, str) and any(
                x in dep_time.lower() for x in ["tbd", "n/a", "unknown"]
            ):
                warnings.append(f"Invalid departure time: {dep_time}")

        return warnings
```

**Estimated Effort:** 3-4 days
**Risk if Not Fixed:** 🟡 MEDIUM - Poor data quality

---

## High Priority Gaps (P1)

### 🟡 6. LLM Output Schema Validation Yok

**Problem:**
```python
# intent_classifier.py:98
result = extract_json_from_text(response.content)
# ❌ No schema validation!
```

**Solution:**

Create `src_v2/validators/schema_validator.py`:

```python
"""Schema validation for LLM outputs."""

from pydantic import BaseModel, validator, Field
from typing import Optional, List, Dict, Any, Literal


class IntentClassificationOutput(BaseModel):
    """Validated schema for intent classification."""

    intent: Literal["plan_trip", "search_flights", "search_hotels",
                    "search_activities", "check_weather", "book", "general"]
    origin: Optional[str] = None
    destination: Optional[str] = None
    departure_date: Optional[str] = None
    return_date: Optional[str] = None
    num_passengers: int = Field(default=1, ge=1, le=20)
    budget: Optional[float] = Field(None, ge=0)
    requires_flights: bool = False
    requires_hotels: bool = False
    requires_activities: bool = False
    requires_weather: bool = False
    preferences: Dict[str, Any] = Field(default_factory=dict)

    @validator('departure_date', 'return_date')
    def validate_date_format(cls, v):
        """Validate ISO date format."""
        if v is None:
            return v

        from datetime import datetime
        try:
            datetime.fromisoformat(v)
        except ValueError:
            raise ValueError(f"Invalid date format: {v}")

        return v


def validate_intent_output(data: dict) -> IntentClassificationOutput:
    """
    Validate LLM intent classification output.

    Raises:
        ValidationError: If output doesn't match schema
    """
    return IntentClassificationOutput(**data)
```

Update `src_v2/nodes/intent_classifier.py`:

```python
from ..validators.schema_validator import validate_intent_output
from pydantic import ValidationError


async def classify_intent_node(state, llm):
    """Classify intent with schema validation."""
    try:
        # ... LLM call ...
        response = await llm.ainvoke(messages)
        result = extract_json_from_text(response.content)

        # ✅ Validate schema
        try:
            validated = validate_intent_output(result)
            result = validated.dict()
        except ValidationError as e:
            return {
                "intent": "general",
                "errors": state.get("errors", []) + [
                    f"LLM output validation failed: {str(e)}"
                ],
                "current_step": "intent_classification",
                "completed_steps": state.get("completed_steps", []) +
                    ["intent_classification_invalid"]
            }

        # Use validated result
        # ...

    except Exception as e:
        # ...
```

**Estimated Effort:** 2 days

---

### 🟡 7. Logging & Observability Yetersiz

**Problem:**
- No structured logging
- No metrics collection
- No performance tracking
- No error aggregation

**Solution:**

Create `src_v2/observability/logger.py`:

```python
"""Structured logging setup."""

import logging
import json
from datetime import datetime
from typing import Any, Dict


class StructuredLogger:
    """Structured logger with JSON output."""

    def __init__(self, name: str):
        """Initialize structured logger."""
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        # JSON formatter
        handler = logging.StreamHandler()
        handler.setFormatter(self.JsonFormatter())
        self.logger.addHandler(handler)

    class JsonFormatter(logging.Formatter):
        """Format logs as JSON."""

        def format(self, record):
            log_data = {
                "timestamp": datetime.utcnow().isoformat(),
                "level": record.levelname,
                "logger": record.name,
                "message": record.getMessage(),
            }

            # Add extra fields
            if hasattr(record, "extra"):
                log_data.update(record.extra)

            return json.dumps(log_data)

    def info(self, message: str, **kwargs):
        """Log info with extra fields."""
        extra = {"extra": kwargs}
        self.logger.info(message, extra=extra)

    def error(self, message: str, **kwargs):
        """Log error with extra fields."""
        extra = {"extra": kwargs}
        self.logger.error(message, extra=extra)

    def warning(self, message: str, **kwargs):
        """Log warning with extra fields."""
        extra = {"extra": kwargs}
        self.logger.warning(message, extra=extra)


# Global logger instance
logger = StructuredLogger("travel_planner_v2")
```

Create `src_v2/observability/metrics.py`:

```python
"""Metrics collection."""

from typing import Dict, Any
from datetime import datetime
import time
from contextlib import contextmanager


class MetricsCollector:
    """Collect performance metrics."""

    def __init__(self):
        """Initialize metrics collector."""
        self.metrics: Dict[str, list] = {
            "latency": [],
            "llm_tokens": [],
            "api_calls": [],
            "errors": [],
            "cache_hits": [],
            "cache_misses": []
        }

    @contextmanager
    def measure_latency(self, operation: str):
        """Context manager to measure operation latency."""
        start = time.time()
        try:
            yield
        finally:
            duration = time.time() - start
            self.metrics["latency"].append({
                "operation": operation,
                "duration_ms": duration * 1000,
                "timestamp": datetime.utcnow().isoformat()
            })

    def record_llm_usage(self, tokens: int, cost: float):
        """Record LLM token usage."""
        self.metrics["llm_tokens"].append({
            "tokens": tokens,
            "cost": cost,
            "timestamp": datetime.utcnow().isoformat()
        })

    def record_api_call(self, service: str, success: bool):
        """Record external API call."""
        self.metrics["api_calls"].append({
            "service": service,
            "success": success,
            "timestamp": datetime.utcnow().isoformat()
        })

    def record_error(self, error_type: str, message: str):
        """Record error."""
        self.metrics["errors"].append({
            "type": error_type,
            "message": message,
            "timestamp": datetime.utcnow().isoformat()
        })

    def record_cache_hit(self, cache_key: str):
        """Record cache hit."""
        self.metrics["cache_hits"].append({
            "key": cache_key,
            "timestamp": datetime.utcnow().isoformat()
        })

    def record_cache_miss(self, cache_key: str):
        """Record cache miss."""
        self.metrics["cache_misses"].append({
            "key": cache_key,
            "timestamp": datetime.utcnow().isoformat()
        })

    def get_summary(self) -> Dict[str, Any]:
        """Get metrics summary."""
        return {
            "total_requests": len(self.metrics["latency"]),
            "avg_latency_ms": sum(m["duration_ms"] for m in self.metrics["latency"]) /
                             max(len(self.metrics["latency"]), 1),
            "total_llm_tokens": sum(m["tokens"] for m in self.metrics["llm_tokens"]),
            "total_llm_cost": sum(m["cost"] for m in self.metrics["llm_tokens"]),
            "total_errors": len(self.metrics["errors"]),
            "cache_hit_rate": len(self.metrics["cache_hits"]) /
                            max(len(self.metrics["cache_hits"]) +
                                len(self.metrics["cache_misses"]), 1)
        }


# Global metrics collector
metrics = MetricsCollector()
```

**Usage:**

```python
from ..observability.logger import logger
from ..observability.metrics import metrics


async def search_flights_node(state, llm, cache):
    """Search flights with logging and metrics."""

    with metrics.measure_latency("flight_search"):
        logger.info(
            "Starting flight search",
            origin=state.get("origin"),
            destination=state.get("destination")
        )

        try:
            # Check cache
            if cache:
                cached = await cache.get_flights(...)
                if cached:
                    metrics.record_cache_hit("flights")
                    logger.info("Cache hit for flight search")
                    return cached
                else:
                    metrics.record_cache_miss("flights")

            # API call
            result = await search_flights.invoke(params)
            metrics.record_api_call("flights", success=True)

            logger.info(
                "Flight search completed",
                num_results=len(result)
            )

            return result

        except Exception as e:
            metrics.record_api_call("flights", success=False)
            metrics.record_error("flight_search", str(e))
            logger.error(
                "Flight search failed",
                error=str(e),
                origin=state.get("origin")
            )
            raise
```

**Estimated Effort:** 3 days

---

## Implementation Roadmap

### Phase 1: Critical Fixes (Week 1-2)
- [ ] Input validation (Day 1-4)
- [ ] Timeout/retry mechanism (Day 5-9)
- [ ] Schema validation (Day 10-12)
- [ ] Basic testing (Day 13-14)

### Phase 2: Caching & Performance (Week 3-4)
- [ ] Redis cache implementation (Day 15-18)
- [ ] Parallel execution (Day 19-21)
- [ ] Session management (Day 22-25)
- [ ] Performance testing (Day 26-28)

### Phase 3: Observability (Week 5)
- [ ] Structured logging (Day 29-30)
- [ ] Metrics collection (Day 31-32)
- [ ] Error tracking (Day 33-34)
- [ ] Monitoring dashboard (Day 35)

### Phase 4: Polish & Deploy (Week 6)
- [ ] Integration testing (Day 36-37)
- [ ] Load testing (Day 38-39)
- [ ] Documentation (Day 40-41)
- [ ] Production deployment (Day 42)

---

## Testing Requirements

### Unit Tests
- [ ] Input validation tests
- [ ] Timeout/retry tests
- [ ] Cache tests
- [ ] Schema validation tests
- [ ] Edge case tests

### Integration Tests
- [ ] End-to-end workflow tests
- [ ] Multi-user scenario tests
- [ ] Error recovery tests
- [ ] Cache invalidation tests

### Performance Tests
- [ ] Load testing (100 concurrent users)
- [ ] Stress testing (500 concurrent users)
- [ ] Latency benchmarks
- [ ] Cost benchmarks

### Security Tests
- [ ] Input sanitization tests
- [ ] Prompt injection tests
- [ ] Rate limiting tests
- [ ] Authentication tests (when added)

---

## Success Metrics

### Performance
- ✅ P95 latency < 3s (currently ~6s)
- ✅ Cache hit rate > 40%
- ✅ API timeout rate < 1%

### Reliability
- ✅ Error rate < 2%
- ✅ Successful retry rate > 80%
- ✅ Uptime > 99.5%

### Cost
- ✅ Cost per request < $0.015 (currently $0.021)
- ✅ LLM token usage < 5000 tokens/request
- ✅ Cache reduces API calls by 40%

---

## Conclusion

This document outlines **25 critical and high-priority gaps** in the current Travel Planner V2 implementation.

**Priority Order:**
1. 🔴 Input Validation (CRITICAL)
2. 🔴 Timeout/Retry (CRITICAL)
3. 🟡 Schema Validation (HIGH)
4. 🟡 Caching (HIGH)
5. 🟡 Parallel Execution (HIGH)
6. 🟡 Observability (HIGH)

**Estimated Total Effort:** 6 weeks (1 engineer)
**MVP Production Ready:** After Phase 1-2 (4 weeks)
**Enterprise Production Ready:** After all phases (6 weeks)

---

**Document maintained by:** Travel Planner Team
**Last updated:** 2025-11-24
**Next review:** 2025-12-01

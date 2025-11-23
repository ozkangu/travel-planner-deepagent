# Travel Planner V2 - MVP Roadmap

## 🎯 Current Status Analysis

### ✅ What We Have (Production-Ready)

**Architecture** ✅
- LangGraph DAG workflow
- Type-safe state management
- Modular node architecture
- Conditional routing
- Error handling framework

**Core Functionality** ✅
- Intent classification (LLM)
- Flight search (mock data)
- Hotel search (mock data)
- Weather forecast (mock data)
- Activity search (mock data)
- Itinerary generation (LLM)

**Developer Experience** ✅
- Comprehensive documentation (3,500+ lines)
- Unit tests (all passing)
- Examples and demos
- Clean code structure
- Easy to extend

### ❌ What's Missing (Critical Gaps)

**1. Real Data Integration** ❌
- Currently using MOCK data for all searches
- No real API integrations (Amadeus, Skyscanner, etc.)
- No actual booking capability

**2. Frontend/UI** ❌
- No user interface
- Command-line only
- No web app or API server

**3. Persistence** ❌
- No database
- No user sessions
- No search history
- No saved itineraries

**4. Authentication** ❌
- No user accounts
- No API authentication
- No rate limiting

**5. Production Infrastructure** ❌
- No deployment setup
- No monitoring/logging
- No caching
- No scaling strategy

---

## 🚦 MVP Priorities (Must-Have vs Nice-to-Have)

### 🔴 CRITICAL (Must Have for MVP)

These are **show-stoppers** - without these, the product doesn't work:

#### 1. Real Flight Search API Integration ⭐⭐⭐⭐⭐
**Why Critical**: Mock data isn't a product
**Effort**: Medium (2-3 days)
**Options**:
- **Amadeus API** (recommended) - Free tier: 2,000 calls/month
- **Skyscanner API** (RapidAPI) - Paid but comprehensive
- **Kiwi.com API** - Good for budget flights
- **Google Flights API** (via SerpAPI) - Easy to use

**Implementation**:
```python
# src_v2/integrations/amadeus_client.py
from amadeus import Client

class AmadeusFlightClient:
    def __init__(self):
        self.client = Client(
            client_id=os.getenv("AMADEUS_CLIENT_ID"),
            client_secret=os.getenv("AMADEUS_CLIENT_SECRET")
        )

    def search_flights(self, origin, destination, date, passengers):
        response = self.client.shopping.flight_offers_search.get(
            originLocationCode=origin,
            destinationLocationCode=destination,
            departureDate=date,
            adults=passengers
        )
        return self.parse_response(response.data)
```

**Status**: ❌ Not Started
**Priority**: P0 (Highest)

---

#### 2. Simple Web API (FastAPI) ⭐⭐⭐⭐⭐
**Why Critical**: Need a way for users to interact
**Effort**: Small (1 day)

**Implementation**:
```python
# api/main.py
from fastapi import FastAPI
from src_v2 import TravelPlannerV2

app = FastAPI(title="Travel Planner API")
planner = TravelPlannerV2()

@app.post("/api/v1/plan-trip")
async def plan_trip(request: TripRequest):
    result = await planner.plan_trip(
        query=request.query,
        origin=request.origin,
        destination=request.destination,
        # ...
    )
    return result

@app.get("/api/v1/health")
def health_check():
    return {"status": "healthy"}
```

**Endpoints Needed**:
- `POST /api/v1/plan-trip` - Full trip planning
- `POST /api/v1/search-flights` - Flights only
- `POST /api/v1/search-hotels` - Hotels only
- `GET /api/v1/health` - Health check

**Status**: ❌ Not Started
**Priority**: P0 (Highest)

---

#### 3. Basic Frontend (Streamlit) ⭐⭐⭐⭐
**Why Critical**: Users need UI, not just API
**Effort**: Small (1 day)

**Why Streamlit**:
- ✅ Fastest to build (MVP in hours)
- ✅ Python-based (same stack)
- ✅ Built-in state management
- ✅ Easy deployment

**Implementation**:
```python
# streamlit_travel_app.py
import streamlit as st
from src_v2 import TravelPlannerV2

st.title("🌍 AI Travel Planner")

# Input form
origin = st.text_input("From", "Istanbul")
destination = st.text_input("To", "Paris")
departure_date = st.date_input("Departure")
return_date = st.date_input("Return")
passengers = st.number_input("Passengers", 1, 10, 1)
budget = st.number_input("Budget ($)", 1000, 50000, 3000)

if st.button("Plan My Trip"):
    with st.spinner("Planning your trip..."):
        planner = TravelPlannerV2()
        result = await planner.plan_trip(
            query=f"Plan trip from {origin} to {destination}",
            origin=origin,
            destination=destination,
            # ...
        )

        st.markdown(result["itinerary"])

        # Show flight options
        st.subheader("✈️ Flight Options")
        for flight in result["flight_options"]:
            st.write(f"{flight['airline']}: ${flight['price']}")
```

**Status**: ⚠️ Partial (streamlit_app.py exists but incomplete)
**Priority**: P0 (Highest)

---

#### 4. Error Handling & Validation ⭐⭐⭐⭐
**Why Critical**: Production systems need robust error handling
**Effort**: Small (1 day)

**What's Needed**:
- Input validation (dates, locations, budget)
- API error handling (rate limits, timeouts)
- Graceful degradation (if one API fails, try another)
- User-friendly error messages

**Implementation**:
```python
# src_v2/utils/validators.py
from datetime import datetime
from typing import Optional

def validate_trip_request(
    origin: str,
    destination: str,
    departure_date: str,
    return_date: Optional[str] = None,
    budget: Optional[float] = None
) -> dict:
    """Validate trip request inputs."""
    errors = []

    # Validate origin/destination
    if not origin or len(origin) < 2:
        errors.append("Invalid origin")

    if not destination or len(destination) < 2:
        errors.append("Invalid destination")

    # Validate dates
    try:
        dep_date = datetime.fromisoformat(departure_date)
        if dep_date < datetime.now():
            errors.append("Departure date must be in the future")
    except ValueError:
        errors.append("Invalid departure date format")

    # Validate return date
    if return_date:
        try:
            ret_date = datetime.fromisoformat(return_date)
            if ret_date <= dep_date:
                errors.append("Return date must be after departure")
        except ValueError:
            errors.append("Invalid return date format")

    # Validate budget
    if budget is not None and budget < 100:
        errors.append("Budget too low (minimum $100)")

    return {
        "valid": len(errors) == 0,
        "errors": errors
    }
```

**Status**: ❌ Not Started
**Priority**: P0 (Highest)

---

#### 5. Deployment Configuration ⭐⭐⭐⭐
**Why Critical**: Need to deploy to production
**Effort**: Small (1 day)

**Options**:
1. **Railway** (Recommended for MVP)
   - ✅ Dead simple deployment
   - ✅ Free tier generous
   - ✅ Auto-deploys from GitHub
   - ✅ Handles env vars

2. **Render**
   - ✅ Free tier
   - ✅ Docker support
   - ✅ Auto SSL

3. **Fly.io**
   - ✅ Global edge deployment
   - ✅ Free tier

**Implementation**:
```dockerfile
# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml uv.lock ./
COPY src_v2/ ./src_v2/
COPY api/ ./api/

# Install dependencies
RUN uv sync --frozen

# Expose port
EXPOSE 8000

# Run API
CMD ["uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# railway.toml
[build]
builder = "DOCKERFILE"

[deploy]
startCommand = "uvicorn api.main:app --host 0.0.0.0 --port $PORT"
healthcheckPath = "/api/v1/health"
```

**Status**: ❌ Not Started
**Priority**: P0 (Highest)

---

### 🟡 IMPORTANT (Should Have for MVP)

These make the product **much better** but not strictly required:

#### 6. Real Hotel Search API ⭐⭐⭐⭐
**Why Important**: Completes the travel planning story
**Effort**: Medium (2 days)
**Options**:
- **Booking.com API** (RapidAPI)
- **Hotels.com API**
- **Expedia TAAP**

**Status**: ❌ Not Started
**Priority**: P1

---

#### 7. Basic Caching (Redis) ⭐⭐⭐
**Why Important**: Save money on API calls, faster responses
**Effort**: Small (1 day)

**Implementation**:
```python
# src_v2/utils/cache.py
import redis
import json
from functools import wraps

redis_client = redis.from_url(os.getenv("REDIS_URL"))

def cache_result(ttl=3600):
    """Cache function result in Redis."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            # Create cache key from function args
            cache_key = f"{func.__name__}:{hash(str(args) + str(kwargs))}"

            # Try to get from cache
            cached = redis_client.get(cache_key)
            if cached:
                return json.loads(cached)

            # Call function
            result = await func(*args, **kwargs)

            # Store in cache
            redis_client.setex(cache_key, ttl, json.dumps(result))

            return result
        return wrapper
    return decorator

# Usage
@cache_result(ttl=1800)  # Cache for 30 minutes
async def search_flights_node(state, llm):
    # ... flight search logic
```

**Status**: ❌ Not Started
**Priority**: P1

---

#### 8. Basic Analytics & Logging ⭐⭐⭐
**Why Important**: Understand usage, debug issues
**Effort**: Small (1 day)

**Implementation**:
```python
# src_v2/utils/analytics.py
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

def log_search(origin, destination, result_count, latency_ms):
    """Log search event."""
    logger.info(
        "search",
        extra={
            "event": "flight_search",
            "origin": origin,
            "destination": destination,
            "result_count": result_count,
            "latency_ms": latency_ms,
            "timestamp": datetime.utcnow().isoformat()
        }
    )

# Use PostHog, Mixpanel, or simple logs
from posthog import Posthog

posthog = Posthog(api_key=os.getenv("POSTHOG_API_KEY"))

def track_trip_planned(user_id, destination, total_cost):
    posthog.capture(
        user_id,
        event="trip_planned",
        properties={
            "destination": destination,
            "total_cost": total_cost
        }
    )
```

**Status**: ❌ Not Started
**Priority**: P1

---

#### 9. Rate Limiting ⭐⭐⭐
**Why Important**: Prevent abuse, control costs
**Effort**: Small (0.5 day)

**Implementation**:
```python
# api/middleware.py
from fastapi import Request
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

@app.post("/api/v1/plan-trip")
@limiter.limit("10/hour")  # 10 requests per hour per IP
async def plan_trip(request: Request, trip_request: TripRequest):
    # ...
```

**Status**: ❌ Not Started
**Priority**: P1

---

#### 10. User Sessions (Optional for MVP) ⭐⭐
**Why Nice**: Better UX, save searches
**Effort**: Medium (2 days)

**Simple Approach**: Use session cookies (no DB yet)
```python
from fastapi import Cookie

@app.post("/api/v1/plan-trip")
async def plan_trip(
    request: TripRequest,
    session_id: str = Cookie(None)
):
    if not session_id:
        session_id = generate_session_id()

    # Store in Redis temporarily
    redis_client.setex(
        f"session:{session_id}",
        3600,
        json.dumps(result)
    )

    return result
```

**Status**: ❌ Not Started
**Priority**: P2 (Nice to have)

---

### 🟢 NICE-TO-HAVE (Post-MVP)

These are **future enhancements**, not needed for initial launch:

- Real-time price monitoring
- Email notifications
- Multi-user accounts with DB
- Payment integration (Stripe)
- Actual booking capability
- Mobile app
- Multi-language support
- ML-based personalization
- NDC airline integration

---

## 📅 Recommended Implementation Timeline

### Week 1: Real Data & Core API
**Goal**: Working API with real flight data

- **Day 1-2**: Amadeus API integration (flights)
  - Sign up for Amadeus
  - Implement flight search
  - Update flight_node.py to use real API
  - Add error handling

- **Day 3**: FastAPI setup
  - Create API endpoints
  - Add request/response models
  - Add health checks

- **Day 4**: Input validation
  - Add validators
  - Add error messages
  - Add unit tests

- **Day 5**: Testing & fixes
  - End-to-end testing
  - Fix bugs
  - Update docs

**Deliverable**: Working API with real flight search

---

### Week 2: Frontend & Deployment
**Goal**: Deployed app users can access

- **Day 6**: Streamlit UI
  - Build form interface
  - Display results nicely
  - Add loading states

- **Day 7**: Hotel API integration
  - Integrate hotel search API
  - Update hotel_node.py
  - Test hotel flow

- **Day 8**: Caching & optimization
  - Add Redis caching
  - Add rate limiting
  - Optimize response times

- **Day 9**: Deployment setup
  - Create Dockerfile
  - Set up Railway/Render
  - Configure env vars
  - Deploy to production

- **Day 10**: Polish & monitoring
  - Add analytics
  - Add logging
  - Test production
  - Write deployment docs

**Deliverable**: Live app at URL users can visit

---

## 🎯 MVP Success Criteria

An MVP is successful if:

✅ **1. Users can plan a real trip**
   - Search real flights (via Amadeus)
   - See real hotel options
   - Get an itinerary

✅ **2. System is accessible**
   - Has a web UI (Streamlit)
   - Has an API (FastAPI)
   - Deployed and online 24/7

✅ **3. System is reliable**
   - Handles errors gracefully
   - Validates inputs
   - Returns results in <10s

✅ **4. System is maintainable**
   - Documented
   - Tested
   - Monitored

---

## 💰 MVP Cost Estimate

### Monthly Operating Costs (MVP)

| Service | Plan | Cost |
|---------|------|------|
| **Hosting** (Railway) | Starter | $5/month |
| **Amadeus API** | Free tier | $0 (2k calls) |
| **OpenRouter + Gemini** | Pay-as-go | ~$10/month (500 requests) |
| **Redis** (Upstash) | Free tier | $0 (10k commands) |
| **Analytics** (PostHog) | Free tier | $0 |
| **Domain** (optional) | Namecheap | $12/year |
| **Total** | | **~$15-20/month** |

**At 1,000 users/month**: Still under $50/month

Very affordable MVP! 💰✅

---

## 🚀 Quick Start Commands (After MVP Implementation)

```bash
# Setup
git clone https://github.com/ozkangu/travel-planner-deepagent.git
cd travel-planner-deepagent
uv sync

# Configure
cp .env.example .env
# Edit .env with API keys:
# - AMADEUS_CLIENT_ID
# - AMADEUS_CLIENT_SECRET
# - OPENROUTER_API_KEY
# - REDIS_URL (optional)

# Run API
uvicorn api.main:app --reload

# Run Streamlit UI
streamlit run streamlit_travel_app.py

# Run tests
pytest test_v2_quick.py

# Deploy to Railway
railway up
```

---

## 📊 MVP vs Full Product Comparison

| Feature | V2 Now | MVP (Week 2) | Full Product (Month 3) |
|---------|--------|--------------|------------------------|
| Flight Search | Mock ❌ | Real API ✅ | Multi-source ✅ |
| Hotel Search | Mock ❌ | Real API ✅ | + Reviews ✅ |
| UI | None ❌ | Streamlit ✅ | React SPA ✅ |
| API | None ❌ | FastAPI ✅ | + GraphQL ✅ |
| Caching | No ❌ | Redis ✅ | + CDN ✅ |
| Auth | No ❌ | No ❌ | Full auth ✅ |
| Booking | No ❌ | No ❌ | Real booking ✅ |
| Payment | No ❌ | No ❌ | Stripe ✅ |
| Analytics | No ❌ | Basic ✅ | Advanced ✅ |
| Mobile | No ❌ | Responsive ⚠️ | Native app ✅ |

---

## 🎯 Recommended Next Actions (Priority Order)

### This Week (Critical - Start Immediately):

1. ✅ **Sign up for Amadeus API** (15 minutes)
   - Go to https://developers.amadeus.com
   - Create account
   - Get API credentials (free tier)

2. ✅ **Create FastAPI skeleton** (2 hours)
   - Basic endpoints
   - Health check
   - Request/response models

3. ✅ **Integrate Amadeus in flight_node.py** (4 hours)
   - Replace mock with real API
   - Add error handling
   - Test thoroughly

4. ✅ **Deploy to Railway** (1 hour)
   - Create Dockerfile
   - Push to Railway
   - Test live endpoint

5. ✅ **Build Streamlit UI** (4 hours)
   - Simple form
   - Display results
   - Deploy to Streamlit Cloud

**Total Time**: ~2 days of focused work
**Result**: WORKING MVP LIVE!

---

## 📝 Files to Create

```
New files needed for MVP:

api/
├── __init__.py
├── main.py              # FastAPI app
├── models.py            # Request/response models
└── middleware.py        # Rate limiting, CORS

src_v2/integrations/
├── __init__.py
├── amadeus_client.py    # Amadeus API wrapper
├── hotel_client.py      # Hotel API wrapper
└── cache.py             # Redis caching

src_v2/utils/
├── validators.py        # Input validation
└── analytics.py         # Logging & tracking

streamlit_travel_app.py  # Streamlit UI (already exists, update)

.env.example             # Environment variables template
Dockerfile               # Container config
railway.toml             # Railway config
pytest.ini               # Test config

docs/
├── API.md               # API documentation
└── DEPLOYMENT.md        # Deployment guide
```

---

## 🎓 Key Learnings for MVP

### What Makes a Good MVP:

✅ **Focus on ONE core use case**
   - "Plan a trip with real flight data" is enough
   - Don't try to do everything

✅ **Real data > Perfect UX**
   - Users will tolerate ugly UI if data is real
   - But won't use pretty UI with fake data

✅ **Deploy early, iterate fast**
   - Get something live ASAP
   - Get user feedback
   - Improve based on reality

✅ **Start with free tiers**
   - Amadeus free tier: 2,000 calls/month
   - Railway free tier: Enough for testing
   - Validate before paying

### Common MVP Mistakes to Avoid:

❌ **Trying to build everything**
   - Don't add 10 features, perfect 1 feature

❌ **Perfectionism**
   - Done is better than perfect
   - You'll rewrite it anyway based on feedback

❌ **No real users**
   - Deploy publicly
   - Share with real people
   - Get feedback early

❌ **Overengineering**
   - Don't need microservices for MVP
   - Monolith is fine
   - Scale later

---

## ✅ Definition of "MVP Ready"

MVP is ready when you can confidently say:

1. ✅ "A stranger can use it without my help"
2. ✅ "It uses real data, not mocks"
3. ✅ "It's deployed and accessible 24/7"
4. ✅ "I'm not embarrassed to share the URL"
5. ✅ "It solves ONE problem well"

If all 5 are true → **Ship it!** 🚀

---

**Status**: 📍 We are at "V2 Complete, MVP Not Started"
**Next Step**: Amadeus API integration (2 days)
**Target**: Live MVP in 2 weeks

Let's build! 💪

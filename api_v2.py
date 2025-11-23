"""
FastAPI REST API for Travel Planner V2.

This provides RESTful endpoints for the LangGraph-based travel planner.

Run with:
    uvicorn api_v2:app --reload --port 8000

Or with custom settings:
    uvicorn api_v2:app --host 0.0.0.0 --port 8080
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List
import asyncio
from datetime import datetime
import os
from dotenv import load_dotenv

from src_v2 import TravelPlannerV2
from src_v2.schemas.state import TravelPlannerState

# Load environment variables
load_dotenv()

# Create FastAPI app
app = FastAPI(
    title="Travel Planner V2 API",
    description="LangGraph-based travel planning API with NDC/ONE Order support",
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Global planner instance (initialized on startup)
planner: Optional[TravelPlannerV2] = None


# Pydantic models for request/response
class TripPlanRequest(BaseModel):
    """Request model for trip planning."""
    query: str = Field(..., description="Natural language trip description")
    origin: Optional[str] = Field(None, description="Departure city")
    destination: Optional[str] = Field(None, description="Destination city")
    departure_date: Optional[str] = Field(None, description="Departure date (YYYY-MM-DD)")
    return_date: Optional[str] = Field(None, description="Return date (YYYY-MM-DD)")
    num_passengers: int = Field(1, ge=1, le=9, description="Number of passengers")
    budget: Optional[float] = Field(None, description="Total budget in USD")
    preferences: Dict[str, Any] = Field(default_factory=dict, description="User preferences")

    class Config:
        json_schema_extra = {
            "example": {
                "query": "Plan a 5-day trip to Tokyo in March",
                "origin": "New York",
                "num_passengers": 2,
                "budget": 5000.0,
                "preferences": {
                    "cabin_class": "economy",
                    "hotel_rating": 4,
                    "activities": ["museums", "restaurants"]
                }
            }
        }


class FlightSearchRequest(BaseModel):
    """Request model for flight search."""
    origin: str = Field(..., description="Departure city")
    destination: str = Field(..., description="Destination city")
    departure_date: str = Field(..., description="Departure date (YYYY-MM-DD)")
    return_date: Optional[str] = Field(None, description="Return date (YYYY-MM-DD)")
    num_passengers: int = Field(1, ge=1, le=9)
    budget: Optional[float] = None


class HotelSearchRequest(BaseModel):
    """Request model for hotel search."""
    destination: str = Field(..., description="Hotel location")
    check_in: str = Field(..., description="Check-in date (YYYY-MM-DD)")
    check_out: str = Field(..., description="Check-out date (YYYY-MM-DD)")
    num_guests: int = Field(1, ge=1, le=9)
    min_rating: float = Field(3.0, ge=1.0, le=5.0)
    budget: Optional[float] = None


class TripPlanResponse(BaseModel):
    """Response model for trip planning."""
    success: bool
    itinerary: Optional[str]
    flight_options: List[Dict[str, Any]]
    hotel_options: List[Dict[str, Any]]
    activity_options: List[Dict[str, Any]]
    weather_forecast: List[Dict[str, Any]]
    total_cost: float
    recommendations: List[str]
    errors: List[str]
    completed_steps: List[str]
    processing_time_seconds: float


class HealthResponse(BaseModel):
    """Health check response."""
    status: str
    timestamp: str
    version: str
    provider: str
    monitoring_enabled: bool


# Startup/shutdown events
@app.on_event("startup")
async def startup_event():
    """Initialize the travel planner on startup."""
    global planner

    provider = os.getenv("LLM_PROVIDER", "anthropic")
    model = os.getenv("LLM_MODEL")

    print(f"🚀 Initializing Travel Planner V2...")
    print(f"   Provider: {provider}")
    print(f"   Model: {model or 'default'}")

    planner = TravelPlannerV2(
        provider=provider,
        model=model,
        verbose=True,
        enable_monitoring=True
    )

    print("✅ Travel Planner V2 initialized successfully")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown."""
    print("👋 Shutting down Travel Planner V2 API")


# API Endpoints
@app.get("/", response_model=HealthResponse)
async def root():
    """Root endpoint with API information."""
    return {
        "status": "online",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "provider": os.getenv("LLM_PROVIDER", "anthropic"),
        "monitoring_enabled": os.getenv("LANGCHAIN_TRACING_V2", "false") == "true"
    }


@app.get("/health", response_model=HealthResponse)
async def health_check():
    """Health check endpoint."""
    if planner is None:
        raise HTTPException(status_code=503, detail="Planner not initialized")

    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "provider": os.getenv("LLM_PROVIDER", "anthropic"),
        "monitoring_enabled": os.getenv("LANGCHAIN_TRACING_V2", "false") == "true"
    }


@app.post("/api/v2/plan-trip", response_model=TripPlanResponse)
async def plan_trip(request: TripPlanRequest):
    """
    Plan a complete trip based on user query.

    This endpoint uses the LangGraph workflow to:
    1. Classify user intent
    2. Search for flights, hotels, activities (in parallel)
    3. Check weather forecast
    4. Generate comprehensive itinerary

    Returns:
        Complete trip plan with all options and recommendations
    """
    if planner is None:
        raise HTTPException(status_code=503, detail="Planner not initialized")

    start_time = asyncio.get_event_loop().time()

    try:
        # Execute workflow
        result: TravelPlannerState = await planner.plan_trip(
            query=request.query,
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            return_date=request.return_date,
            num_passengers=request.num_passengers,
            budget=request.budget,
            preferences=request.preferences
        )

        processing_time = asyncio.get_event_loop().time() - start_time

        return TripPlanResponse(
            success=len(result.get("errors", [])) == 0,
            itinerary=result.get("itinerary"),
            flight_options=result.get("flight_options", []),
            hotel_options=result.get("hotel_options", []),
            activity_options=result.get("activity_options", []),
            weather_forecast=result.get("weather_forecast", []),
            total_cost=result.get("total_cost", 0.0),
            recommendations=result.get("recommendations", []),
            errors=result.get("errors", []),
            completed_steps=result.get("completed_steps", []),
            processing_time_seconds=round(processing_time, 2)
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Planning failed: {str(e)}")


@app.post("/api/v2/search-flights")
async def search_flights(request: FlightSearchRequest):
    """Search for flights only."""
    if planner is None:
        raise HTTPException(status_code=503, detail="Planner not initialized")

    try:
        result = await planner.search_flights(
            origin=request.origin,
            destination=request.destination,
            departure_date=request.departure_date,
            return_date=request.return_date,
            num_passengers=request.num_passengers,
            budget=request.budget
        )

        return {
            "success": True,
            "flight_options": result.get("flight_options", []),
            "errors": result.get("errors", [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Flight search failed: {str(e)}")


@app.post("/api/v2/search-hotels")
async def search_hotels(request: HotelSearchRequest):
    """Search for hotels only."""
    if planner is None:
        raise HTTPException(status_code=503, detail="Planner not initialized")

    try:
        result = await planner.search_hotels(
            destination=request.destination,
            check_in=request.check_in,
            check_out=request.check_out,
            num_guests=request.num_guests,
            min_rating=request.min_rating,
            budget=request.budget
        )

        return {
            "success": True,
            "hotel_options": result.get("hotel_options", []),
            "errors": result.get("errors", [])
        }

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Hotel search failed: {str(e)}")


@app.get("/api/v2/workflow-diagram")
async def get_workflow_diagram():
    """
    Get the workflow diagram in Mermaid format.

    This can be visualized using tools like Mermaid Live Editor.
    """
    if planner is None:
        raise HTTPException(status_code=503, detail="Planner not initialized")

    try:
        # Get mermaid diagram
        mermaid = planner.workflow.get_graph().draw_mermaid()
        return {
            "success": True,
            "diagram": mermaid,
            "viewer_url": "https://mermaid.live/"
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate diagram: {str(e)}")


if __name__ == "__main__":
    import uvicorn

    print("Starting Travel Planner V2 API...")
    uvicorn.run(
        "api_v2:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )

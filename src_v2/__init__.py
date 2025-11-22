"""
Travel Planner V2 - LangGraph-based Travel Planning Agent

A production-ready travel planning system using LangGraph for explicit DAG workflows.

Key improvements over V1:
- Explicit control flow with LangGraph StateGraph
- Conditional routing based on intent
- True parallel execution of independent searches
- Better error handling and retry logic
- Lower latency and cost (fewer LLM calls)
- Easier to debug and monitor
- More predictable behavior
"""

from .travel_planner_v2 import TravelPlannerV2, plan_trip
from .schemas.state import TravelPlannerState

__version__ = "2.0.0"

__all__ = [
    "TravelPlannerV2",
    "plan_trip",
    "TravelPlannerState"
]

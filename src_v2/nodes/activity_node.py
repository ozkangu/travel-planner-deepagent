"""Activity and attraction search node."""

from typing import Dict, Any, List
from langchain_core.language_models import BaseChatModel

from ..schemas.state import TravelPlannerState, ActivityOption


async def search_activities_node(
    state: TravelPlannerState,
    llm: BaseChatModel
) -> Dict[str, Any]:
    """
    Search for activities and attractions at destination.

    This node:
    1. Validates destination
    2. Calls activity search tools
    3. Filters by user interests
    4. Returns curated options
    """
    if not state.get("requires_activities", False):
        return {
            "activity_options": [],
            "completed_steps": state.get("completed_steps", []) + ["activity_search_skipped"]
        }

    destination = state.get("destination")
    preferences = state.get("preferences", {})
    budget = state.get("budget")

    errors = state.get("errors", [])

    if not destination:
        errors.append("Missing destination for activity search")
        return {
            "errors": errors,
            "current_step": "activity_search",
            "completed_steps": state.get("completed_steps", []) + ["activity_search"]
        }

    try:
        # Import activity tools
        from src.tools.activity_tools import search_activities

        # Build search parameters
        search_params = {
            "city": destination
        }

        # Add interest filters if specified
        # Add interest filters if specified
        if "activities" in preferences and isinstance(preferences["activities"], list) and preferences["activities"]:
            # Tool only supports one category, pick the first one
            search_params["category"] = preferences["activities"][0]
        elif "activities" in preferences and isinstance(preferences["activities"], str):
            search_params["category"] = preferences["activities"]

        if budget:
            # Reserve portion for activities
            activity_budget = budget * 0.2  # 20% for activities
            search_params["max_price"] = activity_budget

        # Execute search
        result = search_activities.invoke(search_params)

        # Parse results
        # Parse results
        activity_options: List[ActivityOption] = []

        if isinstance(result, list):
            raw_activities = result
        elif isinstance(result, dict) and ("activities" in result or "options" in result):
            raw_activities = result.get("activities", result.get("options", []))
        else:
            raw_activities = []

        for activity in raw_activities[:10]:  # Top 10 options
            activity_options.append(ActivityOption(
                activity_id=activity.get("activity_id", ""),
                name=activity.get("name", ""),
                type=activity.get("category", ""),
                description=activity.get("description", ""),
                price=activity.get("price", 0.0),
                duration_hours=activity.get("duration_hours", 0.0),
                rating=activity.get("rating", 0.0)
            ))

        return {
            "activity_options": activity_options,
            "current_step": "activity_search",
            "completed_steps": state.get("completed_steps", []) + ["activity_search"],
            "errors": errors
        }

    except Exception as e:
        errors.append(f"Activity search error: {str(e)}")
        return {
            "activity_options": [],
            "errors": errors,
            "current_step": "activity_search",
            "completed_steps": state.get("completed_steps", []) + ["activity_search"]
        }

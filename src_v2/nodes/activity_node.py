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
        from ...src.tools.activity_tools import search_activities

        # Build search parameters
        search_params = {
            "location": destination
        }

        # Add interest filters if specified
        if "activities" in preferences:
            search_params["categories"] = preferences["activities"]

        if "activity_types" in preferences:
            search_params["types"] = preferences["activity_types"]

        if budget:
            # Reserve portion for activities
            activity_budget = budget * 0.2  # 20% for activities
            search_params["max_price"] = activity_budget

        # Execute search
        result = search_activities.invoke(search_params)

        # Parse results
        activity_options: List[ActivityOption] = []

        if "activities" in result or "options" in result:
            raw_activities = result.get("activities", result.get("options", []))
            for activity in raw_activities[:10]:  # Top 10 options
                activity_options.append(ActivityOption(
                    activity_id=activity.get("id", ""),
                    name=activity.get("name", ""),
                    type=activity.get("type", ""),
                    description=activity.get("description", ""),
                    price=activity.get("price", 0.0),
                    duration_hours=activity.get("duration", 0.0),
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

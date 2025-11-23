"""
LangSmith/LangFlow monitoring integration for V2.

This module provides optional monitoring capabilities using LangSmith.
If LANGCHAIN_TRACING_V2 is enabled, all workflow steps will be traced.
"""

import os
from typing import Optional
from contextlib import contextmanager


def is_monitoring_enabled() -> bool:
    """Check if LangSmith monitoring is enabled."""
    return os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"


def get_langsmith_config() -> dict:
    """Get LangSmith configuration from environment."""
    if not is_monitoring_enabled():
        return {}

    return {
        "project_name": os.getenv("LANGCHAIN_PROJECT", "travel-planner-v2"),
        "endpoint": os.getenv("LANGCHAIN_ENDPOINT", "https://api.smith.langchain.com"),
        "api_key": os.getenv("LANGCHAIN_API_KEY"),
    }


@contextmanager
def trace_workflow(workflow_name: str, metadata: Optional[dict] = None):
    """
    Context manager for tracing workflow execution.

    Usage:
        with trace_workflow("travel_planning", {"user_id": "123"}):
            result = await workflow.ainvoke(state)
    """
    if not is_monitoring_enabled():
        yield
        return

    try:
        from langsmith import traceable

        @traceable(name=workflow_name, metadata=metadata)
        def traced_section():
            pass

        traced_section()
        yield
    except ImportError:
        print("⚠️  LangSmith not installed. Install with: pip install langsmith")
        yield
    except Exception as e:
        print(f"⚠️  LangSmith tracing error: {e}")
        yield


def log_workflow_event(event_name: str, data: dict):
    """Log a workflow event to LangSmith."""
    if not is_monitoring_enabled():
        return

    try:
        from langsmith import Client

        client = Client()
        client.create_feedback(
            run_id=data.get("run_id"),
            key=event_name,
            score=1.0,
            comment=str(data)
        )
    except Exception as e:
        print(f"⚠️  Failed to log event {event_name}: {e}")


def setup_monitoring():
    """
    Setup LangSmith monitoring.

    Call this at application startup to ensure monitoring is configured.
    """
    if not is_monitoring_enabled():
        print("ℹ️  LangSmith monitoring is disabled")
        print("   To enable, set LANGCHAIN_TRACING_V2=true in .env")
        return

    config = get_langsmith_config()

    if not config.get("api_key"):
        print("⚠️  LANGCHAIN_API_KEY not set. Monitoring will not work.")
        print("   Get your API key at: https://smith.langchain.com/")
        return

    print("✅ LangSmith monitoring enabled")
    print(f"   Project: {config['project_name']}")
    print(f"   Endpoint: {config['endpoint']}")
    print("   View traces at: https://smith.langchain.com/")

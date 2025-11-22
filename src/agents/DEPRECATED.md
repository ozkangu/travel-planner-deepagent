# DEPRECATED AGENT FILES

**Note:** The individual agent files in this directory are **no longer used** in the current implementation.

## What Changed?

The project has been refactored to use **LangChain's DeepAgent library** (`deepagents`), which uses a different pattern for defining subagents.

### Old Approach (ReAct Agents - DEPRECATED)
```python
from langgraph.prebuilt import create_react_agent

def create_flight_agent(model, provider):
    llm = ChatAnthropic(...)
    agent = create_react_agent(llm, tools=[...], state_modifier=prompt)
    return agent
```

Each agent was a separate file with its own `create_react_agent` instance.

### New Approach (DeepAgent Subagents - CURRENT)
```python
from deepagents import create_deep_agent

subagents = [
    {
        "name": "flight-specialist",
        "description": "Expert in searching and booking flights...",
        "prompt": "You are a specialized flight booking assistant...",
        "tools": [search_flights, get_flight_details],
    },
    # ... more subagents
]

agent = create_deep_agent(
    model=llm,
    system_prompt="You are the Travel Planner Supervisor...",
    subagents=subagents
)
```

Subagents are now defined as **dictionaries** in the main `travel_planner.py` file.

## Why This Change?

DeepAgent provides:
- ✅ **Built-in todo planning** (`write_todos`, `read_todos`)
- ✅ **Filesystem tools** (`read_file`, `write_file`, `edit_file`, `ls`, `grep`, `glob`)
- ✅ **Automatic subagent spawning** via `task` tool
- ✅ **Better context management** - prevents window overflow
- ✅ **Simpler architecture** - no manual StateGraph needed

## Where Is the Current Implementation?

All agent definitions are now in:
- `/src/travel_planner.py` - Main implementation
- `/src/travel_planner_monitored.py` - Monitored version

## Migration Guide

If you were using the old agent files:

**Before:**
```python
from src.agents.flight_agent import create_flight_agent
agent = create_flight_agent(model, provider)
```

**After:**
```python
from src.travel_planner import create_travel_planner
planner = create_travel_planner(provider="anthropic")
```

The planner automatically includes all specialized subagents and can spawn them using the `task` tool.

## Can I Keep These Files?

These files are kept for **reference only**. They show how individual agents were structured, which might be useful for:
- Understanding the tool sets for each domain
- Reference for system prompts
- Educational purposes

However, they are **not imported or used** anywhere in the current codebase.

## Summary

| Aspect | Old (Deprecated) | New (Current) |
|--------|------------------|---------------|
| Location | `src/agents/*.py` | `src/travel_planner.py` |
| Pattern | Individual `create_react_agent` | Subagent dicts in `create_deep_agent` |
| Library | `langgraph.prebuilt` | `deepagents` |
| Routing | Manual StateGraph | Automatic via `task` tool |
| Planning | Manual | Built-in `write_todos` |
| Filesystem | Not available | Built-in file tools |

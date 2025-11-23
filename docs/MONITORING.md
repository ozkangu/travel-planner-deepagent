
# Monitoring & Observability Guide 📊

Complete guide for monitoring agent performance, tracking metrics, and using LangSmith.

## Table of Contents

- [Overview](#overview)
- [Quick Start](#quick-start)
- [Metrics Tracked](#metrics-tracked)
- [LangSmith Integration](#langsmith-integration)
- [Custom Callbacks](#custom-callbacks)
- [Logging](#logging)
- [Examples](#examples)
- [Best Practices](#best-practices)

## Overview

The Travel Planner includes comprehensive monitoring capabilities:

- **Token Usage Tracking**: Monitor tokens consumed by each agent
- **Execution Time**: Track how long each agent takes
- **Cost Estimation**: Estimate API costs based on token usage
- **Tool Analytics**: See which tools are being called
- **Error Tracking**: Capture and log errors
- **LangSmith Integration**: Optional cloud-based observability

## Quick Start

### Basic Monitoring

```python
from src.travel_planner_monitored import create_monitored_travel_planner

# Create planner with monitoring enabled
planner = create_monitored_travel_planner(
    provider="anthropic",
    enable_monitoring=True,  # Enable custom metrics
    log_level="INFO"         # Logging level
)

# Process a request
result = planner.invoke(
    "Find flights from Istanbul to London",
    print_metrics=True  # Print metrics after completion
)

# Access metrics
metrics = result["metrics"]
print(f"Total tokens: {metrics['totals']['total_tokens']}")
print(f"Total cost: ${metrics['totals']['estimated_cost']}")

# Save metrics to file
planner.save_metrics("metrics.json")
```

### Running Monitored Demo

```bash
# Simple demo with metrics
python demo_monitored.py simple

# Interactive demo
python demo_monitored.py interactive

# Comparison demo
python demo_monitored.py comparison
```

## Metrics Tracked

### Per-Agent Metrics

For each agent (flight, hotel, payment, etc.), we track:

```python
{
    "agent_name": "flight",
    "duration_seconds": 2.456,
    "llm_calls": 3,
    "tool_calls": 2,
    "tokens": {
        "prompt_tokens": 1250,
        "completion_tokens": 890,
        "total_tokens": 2140
    },
    "estimated_cost": 0.012450,
    "tool_usage": {
        "search_flights": 1,
        "get_flight_details": 1
    },
    "errors": [],
    "avg_llm_duration": 0.823
}
```

### Session-Wide Metrics

Aggregated metrics across all agents:

```python
{
    "session_duration": 12.34,
    "agents": {
        "flight": {...},
        "hotel": {...},
        ...
    },
    "totals": {
        "llm_calls": 15,
        "tool_calls": 8,
        "total_tokens": 12450,
        "estimated_cost": 0.045670,
        "errors": 0
    }
}
```

## LangSmith Integration

LangSmith provides cloud-based observability with visual traces, analytics, and debugging.

### Setup LangSmith

1. **Get API Key**
   - Visit https://smith.langchain.com/
   - Sign up or log in
   - Go to Settings → API Keys
   - Create a new API key

2. **Configure Environment**

   Add to your `.env` file:
   ```bash
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_api_key_here
   LANGCHAIN_PROJECT=travel-planner-deepagent
   ```

3. **Enable in Code**

   ```python
   planner = create_monitored_travel_planner(
       provider="anthropic",
       enable_langsmith=True  # Enable LangSmith
   )
   ```

### What LangSmith Shows

- **Visual Execution Trace**: See the flow of agent calls as a graph
- **Token Usage**: Per-call and aggregated token metrics
- **Latency Tracking**: Time spent in each component
- **Full Context**: View complete prompts and responses
- **Error Debugging**: Stack traces and error context
- **Run Comparison**: Compare different executions
- **Cost Analytics**: Track spending over time

### Viewing Traces

After running your agent:
1. Go to https://smith.langchain.com/
2. Select your project (`travel-planner-deepagent`)
3. Click on a run to see detailed trace
4. Explore the execution graph, timing, and costs

## Custom Callbacks

### AgentMetricsCallback

Tracks metrics for a single agent:

```python
from src.utils.callbacks import AgentMetricsCallback

# Create callback
callback = AgentMetricsCallback(agent_name="flight")

# Use with LangChain
llm = ChatAnthropic(
    model="claude-3-5-sonnet-20241022",
    callbacks=[callback]
)

# Get metrics
metrics = callback.get_metrics()
callback.print_summary()
```

### MultiAgentMetricsCallback

Aggregates metrics across multiple agents:

```python
from src.utils.callbacks import MultiAgentMetricsCallback

# Create multi-agent callback
multi_callback = MultiAgentMetricsCallback()

# Get callback for each agent
flight_callback = multi_callback.get_agent_callback("flight")
hotel_callback = multi_callback.get_agent_callback("hotel")

# Use callbacks...

# Get all metrics
all_metrics = multi_callback.get_all_metrics()
multi_callback.print_summary()
multi_callback.save_metrics("session_metrics.json")
```

## Logging

### Setup Logging

```python
from src.utils.logging_config import setup_logging

# Configure logging
logger = setup_logging(
    log_level="INFO",      # DEBUG, INFO, WARNING, ERROR, CRITICAL
    log_to_file=True,      # Save logs to file
    log_dir="logs",        # Log directory
    console_output=True    # Print to console
)
```

### Log Levels

- **DEBUG**: Detailed information, tool calls, LLM prompts
- **INFO**: General information, agent starts/ends
- **WARNING**: Warning messages
- **ERROR**: Error messages with stack traces
- **CRITICAL**: Critical failures

### Log Output

Logs include:
- Timestamp
- Log level (color-coded in console)
- Agent name
- Message

Example:
```
2024-11-22 10:30:45 | INFO     | 🚀 flight starting task: Search for flights
2024-11-22 10:30:47 | DEBUG    | 🔧 Calling tool: search_flights
2024-11-22 10:30:48 | INFO     | ✅ flight completed in 2.456s
```

### Log Files

Logs are saved to `logs/travel_planner_YYYYMMDD_HHMMSS.log`

## Examples

### Example 1: Basic Monitoring

```python
from src.travel_planner_monitored import create_monitored_travel_planner

planner = create_monitored_travel_planner(
    enable_monitoring=True,
    log_level="INFO"
)

result = planner.invoke("Find hotels in Paris")

# Metrics are included in result
print(f"Tokens used: {result['metrics']['totals']['total_tokens']}")
```

### Example 2: LangSmith Integration

```python
# Set environment variables first
import os
os.environ["LANGCHAIN_TRACING_V2"] = "true"
os.environ["LANGCHAIN_API_KEY"] = "your_key"

planner = create_monitored_travel_planner(
    enable_langsmith=True
)

# Traces will appear in LangSmith dashboard
result = planner.invoke("Plan a trip to Tokyo")
```

### Example 3: Save Metrics for Analysis

```python
planner = create_monitored_travel_planner(enable_monitoring=True)

queries = [
    "Find flights to Paris",
    "Book a hotel in London",
    "Weather in Tokyo"
]

for i, query in enumerate(queries):
    result = planner.invoke(query, print_metrics=False)
    planner.save_metrics(f"metrics_query_{i}.json")
    planner.reset_metrics()
```

### Example 4: Performance Comparison

```python
from src.travel_planner_monitored import create_monitored_travel_planner

def compare_providers():
    queries = ["Find flights from NYC to SF"]

    for provider in ["anthropic", "openai"]:
        print(f"\nTesting {provider}...")
        planner = create_monitored_travel_planner(
            provider=provider,
            enable_monitoring=True
        )

        result = planner.invoke(queries[0])
        metrics = result["metrics"]

        print(f"Tokens: {metrics['totals']['total_tokens']}")
        print(f"Cost: ${metrics['totals']['estimated_cost']}")
        print(f"Duration: {metrics['session_duration']}s")

compare_providers()
```

## Best Practices

### 1. Always Enable Monitoring in Development

```python
planner = create_monitored_travel_planner(
    enable_monitoring=True,
    log_level="DEBUG"  # Verbose in dev
)
```

### 2. Use LangSmith for Debugging

Enable LangSmith when debugging issues to see full execution traces:

```python
planner = create_monitored_travel_planner(
    enable_langsmith=True,
    log_level="DEBUG"
)
```

### 3. Save Metrics for Analysis

Regularly save metrics to track performance over time:

```python
planner.save_metrics(f"metrics_{datetime.now().isoformat()}.json")
```

### 4. Monitor Costs

Keep track of API costs, especially in production:

```python
result = planner.invoke(query)
cost = result["metrics"]["totals"]["estimated_cost"]

if cost > threshold:
    logger.warning(f"High cost detected: ${cost}")
```

### 5. Use Appropriate Log Levels

- Development: `DEBUG` or `INFO`
- Production: `WARNING` or `ERROR`

### 6. Track Per-Agent Performance

Identify which agents are slow or expensive:

```python
metrics = result["metrics"]
for agent_name, agent_metrics in metrics["agents"].items():
    if agent_metrics["duration_seconds"] > 5:
        print(f"Slow agent: {agent_name}")
```

### 7. Reset Metrics Between Sessions

For accurate per-session metrics:

```python
planner.reset_metrics()
result = planner.invoke(new_query)
```

## Metrics Dashboard (Future)

Coming soon:
- Real-time metrics dashboard
- Historical performance graphs
- Cost tracking over time
- Agent performance comparison
- Alert system for anomalies

## Troubleshooting

### LangSmith Not Working

1. Check API key is set: `echo $LANGCHAIN_API_KEY`
2. Verify tracing is enabled: `echo $LANGCHAIN_TRACING_V2`
3. Check network connection to smith.langchain.com
4. View logs for error messages

### High Token Usage

1. Check which agents are using most tokens
2. Review prompts for inefficiency
3. Consider using shorter context windows
4. Cache repeated queries

### Slow Performance

1. Check agent duration metrics
2. Identify bottleneck agents
3. Review tool call frequency
4. Consider parallel execution

## Advanced Topics

### Custom Metrics

Extend callbacks to track custom metrics:

```python
class CustomMetricsCallback(AgentMetricsCallback):
    def __init__(self, agent_name):
        super().__init__(agent_name)
        self.custom_metric = 0

    def on_custom_event(self):
        self.custom_metric += 1
```

### Metrics Export

Export metrics to external systems:

```python
import json
import requests

metrics = planner.get_metrics()

# Send to monitoring system
requests.post(
    "https://your-monitoring-system.com/metrics",
    json=metrics
)
```

### Real-time Monitoring

Stream metrics during execution:

```python
for update in planner.stream(query):
    current_metrics = planner.get_metrics()
    print(f"Current tokens: {current_metrics['totals']['total_tokens']}")
```

---

**For more information, see:**
- [LangSmith Documentation](https://docs.smith.langchain.com/)
- [LangChain Callbacks](https://python.langchain.com/docs/modules/callbacks/)
- [Main README](README.md)

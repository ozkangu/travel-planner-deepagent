# Travel Planner DeepAgent 🌍✈️

A comprehensive travel planning system built with **LangChain's DeepAgent framework**, featuring specialized AI agents for flight booking, hotel reservations, activities, weather forecasts, and comprehensive monitoring & observability.

## 🎯 Overview

This project demonstrates the power of **LangChain's DeepAgent library** (`deepagents`) by creating a sophisticated multi-agent system for travel planning. The system uses DeepAgent's built-in capabilities including todo planning, filesystem management, and subagent spawning to coordinate specialized travel agents.

### 🌟 What is DeepAgent?

DeepAgent is LangChain's advanced agent framework that goes beyond simple ReAct agents. It includes:

- **📋 Todo Planning**: Automatic task breakdown with `write_todos` and `read_todos` tools
- **📁 Filesystem Backend**: Save context to files (`read_file`, `write_file`, `edit_file`, `ls`, `grep`, `glob`)
- **👥 Subagent Spawning**: Delegate complex tasks to specialized subagents using the `task` tool
- **🧠 Context Management**: Offload large context to prevent window overflow
- **⚡ Complex Task Handling**: Perfect for multi-step, open-ended workflows

## 🏗️ Architecture

The Travel Planner uses **DeepAgent's subagent pattern**:

```
┌─────────────────────────────────────────────┐
│   Travel Planner DeepAgent (Supervisor)     │
│                                             │
│  Built-in Capabilities:                    │
│  • write_todos / read_todos                │
│  • read_file / write_file / edit_file      │
│  • ls / grep / glob                        │
│  • task (subagent spawning)                │
└────────────┬────────────────────────────────┘
             │
    ┌────────┴────────┐
    │  task() tool    │
    └────────┬────────┘
             │
    ┌────────┴────────────────────────────┐
    │                                     │
    ▼                                     ▼
┌──────────────────┐           ┌──────────────────┐
│ flight-specialist│           │ hotel-specialist │
│ (Subagent)       │           │ (Subagent)       │
└──────────────────┘           └──────────────────┘
    ▼                                     ▼
┌──────────────────┐           ┌──────────────────┐
│payment-specialist│           │ancillary-spec... │
│ (Subagent)       │           │ (Subagent)       │
└──────────────────┘           └──────────────────┘
    ▼                                     ▼
┌──────────────────┐           ┌──────────────────┐
│activity-spec...  │           │weather-specialist│
│ (Subagent)       │           │ (Subagent)       │
└──────────────────┘           └──────────────────┘
```

### Specialized Subagents

Each subagent is defined as a dictionary and automatically integrated by DeepAgent:

1. **flight-specialist** ✈️
   - Search for flights between cities
   - Compare prices and options
   - Provide flight details and schedules

2. **hotel-specialist** 🏨
   - Search hotels by location and dates
   - Filter by rating, amenities, and price
   - Show detailed hotel information

3. **payment-specialist** 💳
   - Process booking payments
   - Verify transactions
   - Handle multiple payment methods

4. **ancillary-specialist** 🎒
   - Baggage options and pricing
   - Seat selection
   - Travel insurance
   - Car rental options

5. **activity-specialist** 🎭
   - Recommend tours and attractions
   - Suggest restaurants
   - Provide activity details and booking

6. **weather-specialist** ☀️
   - Weather forecasts
   - Climate information
   - Packing recommendations

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- An Anthropic API key or OpenAI API key

### Installation

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd travel-planner-deepagent
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   This includes the **`deepagents`** library, which is the core framework for this implementation.

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API key:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   # OR
   OPENAI_API_KEY=your_openai_api_key_here
   ```

### Running the Demo

The project includes **two versions**: standard and monitored.

#### Standard Demo (No Monitoring)

#### 1. Simple Demo (Pre-defined Queries)
```bash
python demo.py simple
```
Runs through pre-defined example queries to demonstrate functionality.

#### 2. Interactive Demo (Chat Interface)
```bash
python demo.py interactive
```
Start an interactive conversation with the travel planner.

#### 3. Mock Tools Demo (Direct Tool Testing)
```bash
python demo.py tools
```
Demonstrates each mock tool individually.

Or simply run:
```bash
python demo.py
```
And select the mode interactively.

#### Monitored Demo (With Full Observability) 📊

For monitoring token usage, costs, and performance:

```bash
# Simple demo with metrics
python demo_monitored.py simple

# Interactive demo with monitoring
python demo_monitored.py interactive

# Performance comparison
python demo_monitored.py comparison

# LangSmith setup guide
python demo_monitored.py langsmith
```

**What monitoring provides:**
- Real-time token usage tracking
- Execution time per agent
- Cost estimation
- Tool usage analytics
- Detailed logging
- LangSmith integration (optional)

See [MONITORING.md](MONITORING.md) for complete monitoring guide.

## 📚 Usage Examples

### Basic Flight Search
```python
from src.travel_planner import create_travel_planner

planner = create_travel_planner(provider="anthropic")

result = planner.invoke({
    "messages": [{
        "role": "user",
        "content": "Find me flights from Istanbul to London on December 20th, returning December 27th"
    }]
})
```

### Complex Trip Planning (DeepAgent Shines Here!)
```python
result = planner.invoke({
    "messages": [{
        "role": "user",
        "content": """I'm planning a 7-day trip to Paris in March. Can you help me with:
1. Flights from New York
2. A nice 4-star hotel in central Paris
3. Weather forecast for March
4. Top 5 must-see attractions
5. Restaurant recommendations

Please create a complete itinerary."""
    }]
})
```

**What happens behind the scenes:**
1. DeepAgent uses `write_todos` to break down the plan
2. Uses `task` tool to spawn specialist subagents
3. Saves results to files using `write_file`
4. Aggregates information using `read_file`
5. Presents a comprehensive travel plan

### Getting Weather Information
```python
result = planner.invoke({
    "messages": [{
        "role": "user",
        "content": "What's the weather going to be like in London in late December?"
    }]
})
```

## 🛠️ DeepAgent Implementation Details

### How Subagents Are Defined

Unlike manual StateGraph construction, DeepAgent uses a simple dictionary-based approach:

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
    subagents=subagents,
)
```

### Built-in Tools (Automatic)

DeepAgent automatically provides these tools without explicit configuration:

- **Planning**: `write_todos`, `read_todos`
- **Filesystem**: `read_file`, `write_file`, `edit_file`, `ls`, `grep`, `glob`
- **Delegation**: `task` (for spawning subagents)

### Subagent Spawning

The supervisor can delegate tasks using the `task` tool:

```python
# DeepAgent automatically handles this:
task("flight-specialist", "Find flights from NYC to Paris Dec 20-27")
task("hotel-specialist", "Find 4-star hotels in central Paris")
```

Each subagent runs in isolated context, preventing context window overflow.

## 🔬 DeepAgent vs ReAct Agent

| Feature | DeepAgent (This Repo) | ReAct Agent (Old Approach) |
|---------|----------------------|----------------------------|
| **Library** | `from deepagents import create_deep_agent` | `from langgraph.prebuilt import create_react_agent` |
| **Planning** | ✅ Built-in (`write_todos`) | ❌ Manual implementation |
| **Filesystem** | ✅ Built-in (read/write/edit files) | ❌ Not available |
| **Subagents** | ✅ Automatic spawning via `task` tool | ❌ Manual StateGraph routing |
| **Context Management** | ✅ File-based offloading | ❌ Limited to conversation state |
| **Complex Tasks** | ✅ Excels at multi-step workflows | ⚠️ Suitable for simple tasks |
| **Use Case** | Research, planning, analysis | Simple Q&A, tool calling |

## 🌟 Features

- ✅ True DeepAgent implementation using `deepagents` library
- ✅ Automatic todo planning and task breakdown
- ✅ Filesystem-based context management
- ✅ Subagent spawning for specialized tasks
- ✅ Comprehensive mock data for realistic testing
- ✅ Support for multiple LLM providers (Anthropic, OpenAI)
- ✅ Interactive and programmatic interfaces
- ✅ **Full observability with metrics tracking**
- ✅ **Token usage and cost estimation**
- ✅ **LangSmith integration for visual tracing**
- ✅ **Comprehensive logging system**
- ✅ **Performance monitoring and analytics**

## 🎓 Learning Resources

- [DeepAgent GitHub](https://github.com/langchain-ai/deepagents) - Official DeepAgent repository
- [DeepAgent Documentation](https://docs.langchain.com/oss/python/deepagents/overview) - Official docs
- [DeepAgent Blog Post](https://blog.langchain.com/deep-agents/) - Introduction to DeepAgents
- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/) - LangGraph foundation
- [LangChain Tools](https://python.langchain.com/docs/modules/tools/) - Tool development

## 📝 Notes

- This is a **demonstration project** with mock data
- For production use, replace mock tools with real API integrations
- DeepAgent is ideal for **complex, multi-step tasks**
- For simple Q&A, consider lightweight alternatives
- Implement proper authentication and security measures
- Add persistent storage for bookings and user data

## 🔧 Customization

### Adding New Subagents

Simply add a new dictionary to the `subagents` list:

```python
{
    "name": "visa-specialist",
    "description": "Helps with visa requirements and applications",
    "prompt": "You are a visa requirements specialist...",
    "tools": [check_visa_requirements, get_visa_application_info],
}
```

### Adding New Tools

1. Create tool functions using the `@tool` decorator
2. Add them to the appropriate subagent's tool list

### Switching LLM Providers

```python
# Use Anthropic Claude
planner = create_travel_planner(
    model="claude-sonnet-4-5-20250929",
    provider="anthropic"
)

# Use OpenAI GPT
planner = create_travel_planner(
    model="gpt-4-turbo-preview",
    provider="openai"
)
```

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add new subagents or tools
- Improve existing functionality
- Integrate real APIs
- Enhance the demo scripts
- Improve documentation

## 📄 License

This project is open source and available for educational and demonstration purposes.

## 🙏 Acknowledgments

Built with:
- [DeepAgents](https://github.com/langchain-ai/deepagents) - Advanced agent framework
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent orchestration foundation
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [Anthropic Claude](https://www.anthropic.com/) - Language model
- [OpenAI](https://openai.com/) - Language model

---

**Happy Travels with DeepAgent! 🌍✈️🏨**

*Note: This implementation uses the real `deepagents` library, not `create_react_agent`. For the differences, see the comparison table above.*

# Travel Planner DeepAgent 🌍✈️

A comprehensive travel planning system built with LangGraph's DeepAgent framework, featuring specialized AI agents for flight booking, hotel reservations, activities, weather forecasts, and **comprehensive monitoring & observability**.

## 🎯 Overview

This project demonstrates the power of LangGraph's agent framework by creating a multi-agent system for travel planning. The system uses a supervisor pattern to coordinate specialized agents, each handling different aspects of travel planning.

## 🏗️ Architecture

The Travel Planner uses a **supervisor-based multi-agent architecture**:

```
┌─────────────────────────────────────────────┐
│       Travel Planner Supervisor             │
│    (Coordinates all specialized agents)     │
└────────────┬────────────────────────────────┘
             │
    ┌────────┴────────┐
    │                 │
    ▼                 ▼
┌─────────┐      ┌──────────┐
│ Flight  │      │  Hotel   │
│ Agent   │      │  Agent   │
└─────────┘      └──────────┘
    ▼                 ▼
┌─────────┐      ┌──────────┐
│Payment  │      │Ancillary │
│ Agent   │      │  Agent   │
└─────────┘      └──────────┘
    ▼                 ▼
┌─────────┐      ┌──────────┐
│Activity │      │ Weather  │
│ Agent   │      │  Agent   │
└─────────┘      └──────────┘
```

### Specialized Agents

1. **Flight Agent** ✈️
   - Search for flights between cities
   - Compare prices and options
   - Provide flight details and schedules

2. **Hotel Agent** 🏨
   - Search hotels by location and dates
   - Filter by rating, amenities, and price
   - Show detailed hotel information

3. **Payment Agent** 💳
   - Process booking payments
   - Verify transactions
   - Handle multiple payment methods

4. **Ancillary Agent** 🎒
   - Baggage options and pricing
   - Seat selection
   - Travel insurance
   - Car rental options

5. **Activity Agent** 🎭
   - Recommend tours and attractions
   - Suggest restaurants
   - Provide activity details and booking

6. **Weather Agent** ☀️
   - Weather forecasts
   - Climate information
   - Packing recommendations

## 🚀 Getting Started

### Prerequisites

- Python 3.9 or higher
- An Anthropic API key, OpenAI API key, or OpenRouter API key

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

4. **Set up environment variables**
   ```bash
   cp .env.example .env
   ```

   Edit `.env` and add your API key:
   ```
   ANTHROPIC_API_KEY=your_anthropic_api_key_here
   # OR
   OPENAI_API_KEY=your_openai_api_key_here
   # OR
   OPENROUTER_API_KEY=your_openrouter_api_key_here
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

result = planner.invoke(
    "Find me flights from Istanbul to London on December 20th, returning December 27th"
)
```

### Planning a Complete Trip
```python
result = planner.invoke("""
I'm planning a trip to Paris for 5 days in March.
Can you help me with:
1. Flights from New York
2. A nice 4-star hotel
3. Weather forecast
4. Some must-see attractions
""")
```

### Getting Weather Information
```python
result = planner.invoke(
    "What's the weather going to be like in London in late December?"
)
```

## 🛠️ Mock Tools

All tools return realistic mock data for demonstration purposes. In a production environment, these would be replaced with real API integrations.

### Available Tools

- **Flight Tools**: `search_flights`, `get_flight_details`
- **Hotel Tools**: `search_hotels`, `get_hotel_details`
- **Payment Tools**: `process_payment`, `verify_payment`, `get_payment_methods`
- **Ancillary Tools**: `get_baggage_options`, `get_seat_options`, `get_insurance_options`, `get_car_rental_options`
- **Activity Tools**: `search_activities`, `get_activity_details`, `get_restaurant_recommendations`
- **Weather Tools**: `get_weather_forecast`, `get_climate_info`

## 🏗️ Project Structure

```
travel-planner-deepagent/
├── src/
│   ├── __init__.py
│   ├── travel_planner.py          # Main supervisor agent
│   ├── agents/                     # Specialized agents
│   │   ├── __init__.py
│   │   ├── flight_agent.py
│   │   ├── hotel_agent.py
│   │   ├── payment_agent.py
│   │   ├── ancillary_agent.py
│   │   ├── activity_agent.py
│   │   └── weather_agent.py
│   └── tools/                      # Mock tools
│       ├── __init__.py
│       ├── flight_tools.py
│       ├── hotel_tools.py
│       ├── payment_tools.py
│       ├── ancillary_tools.py
│       ├── activity_tools.py
│       └── weather_tools.py
├── demo.py                         # Demo scripts
├── requirements.txt
├── .env.example
└── README.md
```

## 🔧 Customization

### Adding New Agents

1. Create a new agent file in `src/agents/`
2. Implement the agent using `create_react_agent`
3. Add the agent to the supervisor in `src/travel_planner.py`

### Adding New Tools

1. Create tool functions using the `@tool` decorator
2. Add them to the appropriate agent's tool list
3. Update the agent's system prompt to include the new functionality

### Switching LLM Providers

The system supports Anthropic, OpenAI, and OpenRouter:

```python
# Use Anthropic Claude
planner = create_travel_planner(
    model="claude-3-5-sonnet-20241022",
    provider="anthropic"
)

# Use OpenAI GPT
planner = create_travel_planner(
    model="gpt-4-turbo-preview",
    provider="openai"
)

# Use OpenRouter (access to multiple models)
planner = create_travel_planner(
    model="anthropic/claude-3.5-sonnet",  # or any OpenRouter model
    provider="openrouter"
)
```

## 🌟 Features

- ✅ Multi-agent coordination using LangGraph
- ✅ Specialized agents for different travel tasks
- ✅ Comprehensive mock data for realistic testing
- ✅ Support for multiple LLM providers (Anthropic, OpenAI, OpenRouter)
- ✅ Interactive and programmatic interfaces
- ✅ Extensible architecture for adding new features
- ✅ **Full observability with metrics tracking**
- ✅ **Token usage and cost estimation**
- ✅ **LangSmith integration for visual tracing**
- ✅ **Comprehensive logging system**
- ✅ **Performance monitoring and analytics**

## 🎓 Learning Resources

- [LangGraph Documentation](https://langchain-ai.github.io/langgraph/)
- [LangChain Tools](https://python.langchain.com/docs/modules/tools/)
- [Multi-Agent Systems](https://langchain-ai.github.io/langgraph/tutorials/multi_agent/)

## 📝 Notes

- This is a **demonstration project** with mock data
- For production use, replace mock tools with real API integrations
- Consider adding error handling, retry logic, and rate limiting
- Implement proper authentication and security measures
- Add persistent storage for bookings and user data

## 🤝 Contributing

Contributions are welcome! Feel free to:
- Add new agents or tools
- Improve existing functionality
- Integrate real APIs
- Enhance the demo scripts
- Improve documentation

## 📄 License

This project is open source and available for educational and demonstration purposes.

## 🙏 Acknowledgments

Built with:
- [LangGraph](https://github.com/langchain-ai/langgraph) - Agent framework
- [LangChain](https://github.com/langchain-ai/langchain) - LLM framework
- [Anthropic Claude](https://www.anthropic.com/) - Language model
- [OpenAI](https://openai.com/) - Language model

---

**Happy Travels! 🌍✈️🏨**

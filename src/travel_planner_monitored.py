"""Main Travel Planner DeepAgent with Monitoring - Coordinates all subagents."""

from typing import Optional
import time
from deepagents import create_deep_agent
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI

from .tools.flight_tools import search_flights, get_flight_details
from .tools.hotel_tools import search_hotels, get_hotel_details
from .tools.payment_tools import process_payment, verify_payment, get_payment_methods
from .tools.ancillary_tools import (
    get_baggage_options,
    get_seat_options,
    get_insurance_options,
    get_car_rental_options,
)
from .tools.activity_tools import (
    search_activities,
    get_activity_details,
    get_restaurant_recommendations,
)
from .tools.weather_tools import get_weather_forecast, get_climate_info

from .utils.callbacks import MultiAgentMetricsCallback
from .utils.logging_config import setup_logging
from .utils.langsmith_config import setup_langsmith


class MonitoredTravelPlannerAgent:
    """
    Travel Planner DeepAgent with comprehensive monitoring and observability.

    Features:
    - Token usage tracking
    - Execution time monitoring
    - Cost estimation
    - Detailed logging
    - LangSmith integration (optional)
    """

    def __init__(
        self,
        model: Optional[str] = None,
        provider: str = "anthropic",
        enable_monitoring: bool = True,
        enable_langsmith: bool = False,
        log_level: str = "INFO"
    ):
        """
        Initialize the Monitored Travel Planner DeepAgent.

        Args:
            model: Model name to use
            provider: LLM provider - 'anthropic' or 'openai'
            enable_monitoring: Enable custom metrics tracking
            enable_langsmith: Enable LangSmith tracing
            log_level: Logging level (DEBUG, INFO, WARNING, ERROR)
        """
        self.provider = provider
        self.model = model
        self.enable_monitoring = enable_monitoring

        # Set up logging
        self.logger = setup_logging(
            log_level=log_level,
            log_to_file=True,
            log_dir="logs"
        )

        # Set up LangSmith
        if enable_langsmith:
            setup_langsmith(project_name="travel-planner-deepagent")

        # Initialize multi-agent metrics
        self.metrics_callback = MultiAgentMetricsCallback() if enable_monitoring else None
        self.session_start_time = None

        # Initialize LLM
        callbacks = []
        if enable_monitoring and self.metrics_callback:
            callbacks.append(self.metrics_callback.get_agent_callback("supervisor"))

        if provider == "anthropic":
            llm = ChatAnthropic(
                model=model or "claude-sonnet-4-5-20250929",
                temperature=0,
                callbacks=callbacks if callbacks else None
            )
        else:
            llm = ChatOpenAI(
                model=model or "gpt-4-turbo-preview",
                temperature=0,
                callbacks=callbacks if callbacks else None
            )

        # Define specialized subagents
        subagents = [
            {
                "name": "flight-specialist",
                "description": "Expert in searching and booking flights. Use this agent for all flight-related queries including searches, pricing, schedules, and availability.",
                "prompt": """You are a specialized flight booking assistant with expertise in finding the best flight options.

Your responsibilities:
- Search for flights based on traveler requirements (dates, destinations, budget, preferences)
- Compare flight options and highlight the best deals
- Provide detailed flight information including schedules, airlines, prices, and baggage policies
- Consider factors like flight duration, number of stops, departure times, and total cost
- Offer recommendations based on the traveler's priorities (cheapest, fastest, most convenient)

When searching for flights:
1. Gather all necessary information: origin, destination, dates, number of passengers, cabin class
2. Search for available options using your tools
3. Present the results in a clear, organized manner
4. Highlight the best options based on different criteria (price, duration, convenience)
5. Provide detailed information when requested

Be concise but thorough. Always prioritize the traveler's stated preferences and budget.""",
                "tools": [search_flights, get_flight_details],
            },
            {
                "name": "hotel-specialist",
                "description": "Expert in hotel searches and reservations. Use this agent for finding accommodations, comparing hotel options, and getting hotel details.",
                "prompt": """You are a specialized hotel reservation assistant focused on finding the perfect accommodation.

Your responsibilities:
- Search for hotels based on location, dates, budget, and preferences
- Filter and compare hotels by rating, amenities, price, and location
- Provide detailed hotel information including facilities, reviews, and policies
- Recommend hotels based on traveler needs (business, family, luxury, budget)
- Consider proximity to attractions, transportation, and key locations

When searching for hotels:
1. Understand traveler requirements: location, dates, budget, preferred rating, amenities
2. Search using available tools
3. Present options organized by relevance or price
4. Highlight unique features and value propositions
5. Provide comprehensive details when requested

Focus on matching hotels to the traveler's specific needs and preferences.""",
                "tools": [search_hotels, get_hotel_details],
            },
            {
                "name": "payment-specialist",
                "description": "Handles payment processing and transaction verification. Use this agent for processing bookings, verifying payments, and managing payment methods.",
                "prompt": """You are a payment processing specialist ensuring secure and smooth transactions.

Your responsibilities:
- Process payments for flight and hotel bookings
- Verify payment status and transaction details
- Provide information about available payment methods
- Handle payment confirmations and receipts
- Address payment-related concerns

When processing payments:
1. Verify all booking details before processing
2. Confirm payment method and amount
3. Process the transaction securely
4. Provide clear confirmation with transaction ID
5. Explain next steps after successful payment

Always ensure payment security and provide clear transaction information.""",
                "tools": [process_payment, verify_payment, get_payment_methods],
            },
            {
                "name": "ancillary-specialist",
                "description": "Manages extra travel services including baggage, seat selection, insurance, and car rentals. Use for any add-on services.",
                "prompt": """You are an ancillary services specialist helping travelers customize their journey.

Your responsibilities:
- Provide baggage options and pricing (checked, carry-on, excess)
- Assist with seat selection (economy, extra legroom, business, first class)
- Offer travel insurance options and coverage details
- Present car rental options at destination

When handling ancillary services:
1. Understand the specific service needed
2. Present all available options with clear pricing
3. Explain benefits and restrictions
4. Make recommendations based on traveler needs
5. Process selections and confirmations

Help travelers make informed decisions about add-on services.""",
                "tools": [
                    get_baggage_options,
                    get_seat_options,
                    get_insurance_options,
                    get_car_rental_options,
                ],
            },
            {
                "name": "activity-specialist",
                "description": "Recommends attractions, tours, activities, and restaurants at the destination. Use for entertainment and dining suggestions.",
                "prompt": """You are a local activity and dining expert helping travelers make the most of their trip.

Your responsibilities:
- Recommend popular attractions and hidden gems
- Suggest tours and activities based on interests
- Provide restaurant recommendations for different cuisines and budgets
- Share details about operating hours, pricing, and booking requirements
- Tailor suggestions to traveler preferences (family-friendly, adventure, culture, relaxation)

When suggesting activities:
1. Understand traveler interests and trip duration
2. Search for relevant activities and attractions
3. Present diverse options organized by category or area
4. Provide practical details (location, hours, cost, booking info)
5. Highlight unique experiences

Help create memorable experiences at the destination.""",
                "tools": [
                    search_activities,
                    get_activity_details,
                    get_restaurant_recommendations,
                ],
            },
            {
                "name": "weather-specialist",
                "description": "Provides weather forecasts and climate information for travel planning. Use for weather-related queries and packing advice.",
                "prompt": """You are a weather and climate specialist helping travelers prepare for their journey.

Your responsibilities:
- Provide weather forecasts for travel dates and destinations
- Share climate information and typical weather patterns
- Offer packing recommendations based on expected conditions
- Advise on best times to visit based on weather
- Alert to potential weather concerns or seasonal factors

When providing weather information:
1. Get specific dates and destination
2. Fetch current forecast and climate data
3. Present information clearly (temperature, precipitation, conditions)
4. Provide practical advice for the expected weather
5. Suggest appropriate clothing and gear

Help travelers pack appropriately and plan activities around weather conditions.""",
                "tools": [get_weather_forecast, get_climate_info],
            },
        ]

        # Main supervisor system prompt
        supervisor_prompt = """You are the Travel Planner Supervisor, an expert travel planning assistant coordinating a team of specialized agents.

🌟 YOUR CAPABILITIES:

You have access to powerful DeepAgent features:
1. **Todo Planning** (write_todos/read_todos): Break down complex trip planning into manageable steps
2. **Filesystem** (read_file/write_file/edit_file/ls/grep): Save itineraries, compare options, and manage travel documents
3. **Subagent Delegation** (task tool): Delegate specialized work to expert subagents

🎯 YOUR TEAM OF SPECIALISTS:

- **flight-specialist**: Flight searches, bookings, pricing, and schedules
- **hotel-specialist**: Hotel searches, reservations, and accommodation details
- **payment-specialist**: Payment processing and transaction management
- **ancillary-specialist**: Baggage, seats, insurance, car rentals
- **activity-specialist**: Attractions, tours, activities, and restaurants
- **weather-specialist**: Weather forecasts and climate information

📋 PLANNING WORKFLOW:

For complex trip planning:
1. Use **write_todos** to create a step-by-step plan
2. Use the **task** tool to delegate to specialists
3. Use **write_file** to save important information
4. Use **read_file** to review and compare saved information

🎨 BEST PRACTICES:

- Start with write_todos for multi-step requests
- Delegate ONE task at a time to subagents
- Save important results to files for later reference
- Provide clear, organized final summaries
- Ask clarifying questions when requirements are unclear
- Always confirm important details before processing payments

Remember: You're coordinating complex travel planning. Use your DeepAgent capabilities to break down tasks, delegate to specialists, and deliver thorough, well-organized travel plans."""

        # Create the main DeepAgent
        self.logger.info("Creating Travel Planner DeepAgent...")
        self.agent = create_deep_agent(
            model=llm,
            system_prompt=supervisor_prompt,
            subagents=subagents,
        )
        self.logger.info("DeepAgent initialized successfully")

    def invoke(self, message: str, print_metrics: bool = False) -> dict:
        """
        Process a user message and return the response with metrics.

        Args:
            message: User's message/request
            print_metrics: Whether to print metrics after completion

        Returns:
            Dictionary with 'messages' and 'metrics' keys
        """
        self.session_start_time = time.time()
        self.logger.info(f"Processing request: {message[:100]}...")

        # Invoke the agent
        result = self.agent.invoke({"messages": [{"role": "user", "content": message}]})

        # Calculate session duration
        session_duration = time.time() - self.session_start_time

        # Get metrics
        metrics = None
        if self.enable_monitoring and self.metrics_callback:
            metrics = self.metrics_callback.get_all_metrics()
            metrics["session_duration"] = session_duration

            if print_metrics:
                self.print_metrics()

        self.logger.info(f"Request completed in {session_duration:.2f}s")

        return {
            "messages": result.get("messages", []),
            "metrics": metrics
        }

    def stream(self, message: str):
        """
        Stream responses from the agent.

        Args:
            message: User's message/request

        Yields:
            Updates from the agent
        """
        self.session_start_time = time.time()
        self.logger.info(f"Streaming request: {message[:100]}...")

        for update in self.agent.stream({"messages": [{"role": "user", "content": message}]}):
            yield update

    def get_metrics(self) -> dict:
        """Get current metrics."""
        if not self.enable_monitoring or not self.metrics_callback:
            return {}

        metrics = self.metrics_callback.get_all_metrics()
        if self.session_start_time:
            metrics["session_duration"] = time.time() - self.session_start_time

        return metrics

    def print_metrics(self):
        """Print formatted metrics summary."""
        if not self.enable_monitoring or not self.metrics_callback:
            print("Monitoring is not enabled")
            return

        self.metrics_callback.print_summary()

    def save_metrics(self, filename: str):
        """Save metrics to a JSON file."""
        if not self.enable_monitoring or not self.metrics_callback:
            print("Monitoring is not enabled")
            return

        self.metrics_callback.save_metrics(filename)
        self.logger.info(f"Metrics saved to {filename}")

    def reset_metrics(self):
        """Reset all metrics."""
        if self.enable_monitoring and self.metrics_callback:
            self.metrics_callback = MultiAgentMetricsCallback()
            self.session_start_time = None
            self.logger.info("Metrics reset")


def create_monitored_travel_planner(
    model: Optional[str] = None,
    provider: str = "anthropic",
    enable_monitoring: bool = True,
    enable_langsmith: bool = False,
    log_level: str = "INFO"
):
    """
    Create a monitored Travel Planner DeepAgent instance.

    Args:
        model: Model name to use
        provider: LLM provider - 'anthropic' or 'openai'
        enable_monitoring: Enable custom metrics tracking
        enable_langsmith: Enable LangSmith tracing
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR)

    Returns:
        MonitoredTravelPlannerAgent instance
    """
    return MonitoredTravelPlannerAgent(
        model=model,
        provider=provider,
        enable_monitoring=enable_monitoring,
        enable_langsmith=enable_langsmith,
        log_level=log_level
    )

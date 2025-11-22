"""Main Travel Planner Agent with Monitoring - Coordinates all subagents."""

from typing import Annotated, Literal, TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage
import time

from .agents.flight_agent import create_flight_agent
from .agents.hotel_agent import create_hotel_agent
from .agents.payment_agent import create_payment_agent
from .agents.ancillary_agent import create_ancillary_agent
from .agents.activity_agent import create_activity_agent
from .agents.weather_agent import create_weather_agent

from .utils.callbacks import AgentMetricsCallback, MultiAgentMetricsCallback
from .utils.logging_config import setup_logging, get_agent_logger, log_agent_start, log_agent_end
from .utils.langsmith_config import setup_langsmith


# Define the state
class TravelPlannerState(TypedDict):
    """State for the travel planner agent."""
    messages: Annotated[list[BaseMessage], add_messages]
    next_agent: Optional[str]


class MonitoredTravelPlannerAgent:
    """
    Travel Planner Agent with comprehensive monitoring and observability.

    Features:
    - Token usage tracking per agent
    - Execution time monitoring
    - Cost estimation
    - Tool usage analytics
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
        Initialize the Monitored Travel Planner Agent.

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

        # Initialize LLM for supervisor
        callbacks = [self.metrics_callback.get_agent_callback("supervisor")] if enable_monitoring else []

        if provider == "anthropic":
            self.llm = ChatAnthropic(
                model=model or "claude-3-5-sonnet-20241022",
                temperature=0,
                callbacks=callbacks
            )
        else:
            self.llm = ChatOpenAI(
                model=model or "gpt-4-turbo-preview",
                temperature=0,
                callbacks=callbacks
            )

        # Create specialized agents with monitoring
        self.logger.info("Initializing specialized agents...")
        self.agents = self._create_monitored_agents()

        # Build the graph
        self.graph = self._build_graph()
        self.logger.info("✅ Travel Planner Agent initialized successfully")

    def _create_monitored_agents(self):
        """Create all specialized agents with monitoring callbacks."""
        agents = {}
        agent_names = ["flight", "hotel", "payment", "ancillary", "activity", "weather"]

        agent_factories = {
            "flight": create_flight_agent,
            "hotel": create_hotel_agent,
            "payment": create_payment_agent,
            "ancillary": create_ancillary_agent,
            "activity": create_activity_agent,
            "weather": create_weather_agent,
        }

        for agent_name in agent_names:
            # Get callback for this agent
            callback = self.metrics_callback.get_agent_callback(agent_name) if self.enable_monitoring else None

            # Create agent with callback
            agents[agent_name] = agent_factories[agent_name](
                model=self.model,
                provider=self.provider
            )

            self.logger.debug(f"✓ {agent_name} agent created")

        return agents

    def _build_graph(self):
        """Build the agent coordination graph."""
        workflow = StateGraph(TravelPlannerState)

        # Add supervisor node
        workflow.add_node("supervisor", self._supervisor_node)

        # Add agent nodes
        for agent_name in self.agents.keys():
            workflow.add_node(agent_name, self._create_agent_node(agent_name))

        # Add edges
        workflow.add_edge(START, "supervisor")

        # Conditional edges from supervisor
        workflow.add_conditional_edges(
            "supervisor",
            self._route_to_agent,
            {
                "flight": "flight",
                "hotel": "hotel",
                "payment": "payment",
                "ancillary": "ancillary",
                "activity": "activity",
                "weather": "weather",
                "end": END
            }
        )

        # Edges back to supervisor
        for agent_name in self.agents.keys():
            workflow.add_edge(agent_name, "supervisor")

        return workflow.compile()

    def _supervisor_node(self, state: TravelPlannerState) -> TravelPlannerState:
        """Supervisor node that decides which agent to call next."""
        messages = state["messages"]

        # System prompt
        system_prompt = """You are the Travel Planner Supervisor, coordinating a team of specialized travel agents.

Your team consists of:
- flight: Handles flight searches and booking
- hotel: Handles hotel searches and booking
- payment: Processes payments and transactions
- ancillary: Handles extra services (baggage, seats, insurance, car rentals)
- activity: Recommends activities, attractions, and restaurants
- weather: Provides weather forecasts and climate information

Your job is to:
1. Understand what the traveler needs
2. Decide which specialist agent should handle the request
3. Coordinate the work between different agents
4. Provide a final summary when all tasks are complete

When you receive a message, determine which agent should handle it. If the request is complete, respond with "FINISHED" to end the conversation."""

        routing_prompt = f"""{system_prompt}

Based on the conversation, which agent should handle the next task?

Respond with one of: flight, hotel, payment, ancillary, activity, weather, or FINISHED

Conversation so far:
{self._format_messages(messages[-5:])}

Which agent should handle the next task? If the task is complete, say FINISHED."""

        # Call LLM
        start_time = time.time()
        response = self.llm.invoke([HumanMessage(content=routing_prompt)])
        duration = time.time() - start_time

        self.logger.debug(f"Supervisor routing decision took {duration:.3f}s")

        # Parse response
        content = response.content.strip().lower()

        if "finished" in content or "complete" in content:
            next_agent = "end"
            state["messages"].append(
                AIMessage(content="Is there anything else you'd like help with for your trip?")
            )
        elif "flight" in content:
            next_agent = "flight"
        elif "hotel" in content:
            next_agent = "hotel"
        elif "payment" in content:
            next_agent = "payment"
        elif "ancillary" in content or "baggage" in content or "seat" in content:
            next_agent = "ancillary"
        elif "activity" in content or "restaurant" in content:
            next_agent = "activity"
        elif "weather" in content or "climate" in content:
            next_agent = "weather"
        else:
            next_agent = "end"

        state["next_agent"] = next_agent
        self.logger.info(f"Supervisor routing to: {next_agent}")

        return state

    def _create_agent_node(self, agent_name: str):
        """Create a node function for a specific agent."""

        def agent_node(state: TravelPlannerState) -> TravelPlannerState:
            """Execute the specified agent."""
            start_time = time.time()
            log_agent_start(self.logger, agent_name, "Processing user request")

            agent = self.agents[agent_name]
            messages = state["messages"]

            # Set current agent for metrics
            if self.metrics_callback:
                self.metrics_callback.set_current_agent(agent_name)

            # Invoke agent
            result = agent.invoke({"messages": messages})

            # Add response to state
            state["messages"].extend(result["messages"][len(messages):])

            duration = time.time() - start_time
            log_agent_end(self.logger, agent_name, duration)

            return state

        return agent_node

    def _route_to_agent(self, state: TravelPlannerState) -> str:
        """Route to the appropriate agent."""
        return state.get("next_agent", "end")

    def _format_messages(self, messages: list[BaseMessage]) -> str:
        """Format messages for display."""
        formatted = []
        for msg in messages:
            if isinstance(msg, HumanMessage):
                formatted.append(f"User: {msg.content}")
            elif isinstance(msg, AIMessage):
                formatted.append(f"Assistant: {msg.content}")
        return "\n".join(formatted)

    def invoke(self, message: str, print_metrics: bool = True) -> dict:
        """
        Process a user message and return the response.

        Args:
            message: User's message/request
            print_metrics: Whether to print metrics after completion

        Returns:
            Response from the agent with metrics
        """
        self.logger.info(f"Processing request: {message[:80]}...")

        initial_state = {
            "messages": [HumanMessage(content=message)],
            "next_agent": None
        }

        # Reset metrics for new session
        if self.metrics_callback:
            for callback in self.metrics_callback.agent_metrics.values():
                callback.reset()

        # Execute
        start_time = time.time()
        result = self.graph.invoke(initial_state)
        total_duration = time.time() - start_time

        self.logger.info(f"✅ Request completed in {total_duration:.3f}s")

        # Print metrics
        if self.enable_monitoring and print_metrics:
            self.metrics_callback.print_summary()

        # Add metrics to result
        if self.enable_monitoring:
            result["metrics"] = self.metrics_callback.get_all_metrics()

        return result

    def stream(self, message: str):
        """Stream responses from the agent."""
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "next_agent": None
        }

        for update in self.graph.stream(initial_state):
            yield update

    def get_metrics(self) -> dict:
        """Get current metrics."""
        if self.enable_monitoring:
            return self.metrics_callback.get_all_metrics()
        return {}

    def save_metrics(self, filepath: str):
        """Save metrics to file."""
        if self.enable_monitoring:
            self.metrics_callback.save_metrics(filepath)

    def reset_metrics(self):
        """Reset all metrics."""
        if self.enable_monitoring:
            self.metrics_callback = MultiAgentMetricsCallback()


def create_monitored_travel_planner(
    model: Optional[str] = None,
    provider: str = "anthropic",
    enable_monitoring: bool = True,
    enable_langsmith: bool = False,
    log_level: str = "INFO"
):
    """
    Create a monitored Travel Planner Agent instance.

    Args:
        model: Model name to use
        provider: LLM provider - 'anthropic' or 'openai'
        enable_monitoring: Enable custom metrics tracking
        enable_langsmith: Enable LangSmith tracing
        log_level: Logging level

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

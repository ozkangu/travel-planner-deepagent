"""Main Travel Planner Agent - Coordinates all subagents."""

from typing import Annotated, Literal, TypedDict, Optional
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
from langgraph.prebuilt import create_react_agent
from langchain_anthropic import ChatAnthropic
from langchain_openai import ChatOpenAI
from langchain_core.messages import BaseMessage, HumanMessage, AIMessage

from .agents.flight_agent import create_flight_agent
from .agents.hotel_agent import create_hotel_agent
from .agents.payment_agent import create_payment_agent
from .agents.ancillary_agent import create_ancillary_agent
from .agents.activity_agent import create_activity_agent
from .agents.weather_agent import create_weather_agent


# Define the state
class TravelPlannerState(TypedDict):
    """State for the travel planner agent."""
    messages: Annotated[list[BaseMessage], add_messages]
    next_agent: Optional[str]


class TravelPlannerAgent:
    """
    Main Travel Planner Agent that coordinates specialized subagents.

    This agent acts as a supervisor, delegating tasks to specialized agents:
    - FlightAgent: Flight search and booking
    - HotelAgent: Hotel search and booking
    - PaymentAgent: Payment processing
    - AncillaryAgent: Extra services (baggage, seats, insurance, car rental)
    - ActivityAgent: Activities and restaurant recommendations
    - WeatherAgent: Weather forecasts and climate information
    """

    def __init__(self, model: Optional[str] = None, provider: str = "anthropic"):
        """
        Initialize the Travel Planner Agent.

        Args:
            model: Model name to use
            provider: LLM provider - 'anthropic' or 'openai'
        """
        self.provider = provider
        self.model = model

        # Initialize LLM for supervisor
        if provider == "anthropic":
            self.llm = ChatAnthropic(
                model=model or "claude-3-5-sonnet-20241022",
                temperature=0
            )
        else:
            self.llm = ChatOpenAI(
                model=model or "gpt-4-turbo-preview",
                temperature=0
            )

        # Create specialized agents
        self.agents = {
            "flight": create_flight_agent(model, provider),
            "hotel": create_hotel_agent(model, provider),
            "payment": create_payment_agent(model, provider),
            "ancillary": create_ancillary_agent(model, provider),
            "activity": create_activity_agent(model, provider),
            "weather": create_weather_agent(model, provider),
        }

        # Build the graph
        self.graph = self._build_graph()

    def _build_graph(self):
        """Build the agent coordination graph."""

        workflow = StateGraph(TravelPlannerState)

        # Add supervisor node
        workflow.add_node("supervisor", self._supervisor_node)

        # Add agent nodes
        for agent_name in self.agents.keys():
            workflow.add_node(agent_name, self._create_agent_node(agent_name))

        # Add edges from supervisor to each agent
        workflow.add_edge(START, "supervisor")

        # Define conditional edges from supervisor
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

        # Add edges back to supervisor from each agent
        for agent_name in self.agents.keys():
            workflow.add_edge(agent_name, "supervisor")

        return workflow.compile()

    def _supervisor_node(self, state: TravelPlannerState) -> TravelPlannerState:
        """
        Supervisor node that decides which agent to call next.

        This node analyzes the conversation and determines which specialized
        agent should handle the next task.
        """

        messages = state["messages"]

        # System prompt for the supervisor
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

When you receive a message, determine which agent should handle it. If the request is complete, respond with "FINISHED" to end the conversation.

Always think about what the traveler needs next and route to the appropriate specialist."""

        # Create a prompt asking which agent to use
        routing_prompt = f"""{system_prompt}

Based on the conversation, which agent should handle the next task?

Respond with one of: flight, hotel, payment, ancillary, activity, weather, or FINISHED

Conversation so far:
{self._format_messages(messages[-5:])}  # Last 5 messages for context

Which agent should handle the next task? If the task is complete and you need to provide a final response, say FINISHED."""

        # Use LLM to decide routing
        response = self.llm.invoke([HumanMessage(content=routing_prompt)])

        # Parse response to get next agent
        content = response.content.strip().lower()

        # Simple parsing logic
        if "finished" in content or "complete" in content:
            next_agent = "end"
            # Add a final message
            state["messages"].append(
                AIMessage(content="Is there anything else you'd like help with for your trip?")
            )
        elif "flight" in content:
            next_agent = "flight"
        elif "hotel" in content:
            next_agent = "hotel"
        elif "payment" in content:
            next_agent = "payment"
        elif "ancillary" in content or "baggage" in content or "seat" in content or "insurance" in content or "car" in content:
            next_agent = "ancillary"
        elif "activity" in content or "activities" in content or "restaurant" in content or "things to do" in content:
            next_agent = "activity"
        elif "weather" in content or "climate" in content:
            next_agent = "weather"
        else:
            # Default to a general response
            next_agent = "end"

        state["next_agent"] = next_agent
        return state

    def _create_agent_node(self, agent_name: str):
        """Create a node function for a specific agent."""

        def agent_node(state: TravelPlannerState) -> TravelPlannerState:
            """Execute the specified agent."""
            agent = self.agents[agent_name]

            # Get the last user message
            messages = state["messages"]

            # Invoke the agent
            result = agent.invoke({"messages": messages})

            # Add agent's response to state
            state["messages"].extend(result["messages"][len(messages):])

            return state

        return agent_node

    def _route_to_agent(self, state: TravelPlannerState) -> str:
        """Route to the appropriate agent based on supervisor's decision."""
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

    def invoke(self, message: str) -> dict:
        """
        Process a user message and return the response.

        Args:
            message: User's message/request

        Returns:
            Response from the agent
        """
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "next_agent": None
        }

        result = self.graph.invoke(initial_state)
        return result

    def stream(self, message: str):
        """
        Stream responses from the agent.

        Args:
            message: User's message/request

        Yields:
            Updates from the agent
        """
        initial_state = {
            "messages": [HumanMessage(content=message)],
            "next_agent": None
        }

        for update in self.graph.stream(initial_state):
            yield update


def create_travel_planner(model: Optional[str] = None, provider: str = "anthropic"):
    """
    Create a Travel Planner Agent instance.

    Args:
        model: Model name to use
        provider: LLM provider - 'anthropic' or 'openai'

    Returns:
        TravelPlannerAgent instance
    """
    return TravelPlannerAgent(model=model, provider=provider)

"""
Streamlit Chat Interface for Travel Planner V2.

This provides an interactive chat interface with:
- Context preservation across messages
- Conversation history
- Real-time streaming (optional)
- Session state management

Run with:
    streamlit run streamlit_chat_v2.py
"""

import streamlit as st
import asyncio
from datetime import datetime
from typing import List, Dict, Any
import os
from dotenv import load_dotenv

from src_v2 import TravelPlannerV2
from src_v2.schemas.state import TravelPlannerState

# Load environment variables
load_dotenv()

# Page configuration
st.set_page_config(
    page_title="Travel Planner V2 - Chat",
    page_icon="✈️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .stChatMessage {
        padding: 1rem;
        border-radius: 0.5rem;
    }
    .user-message {
        background-color: #e3f2fd;
    }
    .assistant-message {
        background-color: #f5f5f5;
    }
    .metadata {
        font-size: 0.8rem;
        color: #666;
        margin-top: 0.5rem;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
def init_session_state():
    """Initialize session state variables."""
    if "messages" not in st.session_state:
        st.session_state.messages = []

    if "conversation_context" not in st.session_state:
        st.session_state.conversation_context = {
            "origin": None,
            "destination": None,
            "departure_date": None,
            "return_date": None,
            "num_passengers": 1,
            "budget": None,
            "preferences": {},
            "last_state": None
        }

    if "planner" not in st.session_state:
        st.session_state.planner = None

    if "conversation_id" not in st.session_state:
        st.session_state.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")


def initialize_planner(provider: str, model: str = None, enable_monitoring: bool = True):
    """Initialize the travel planner."""
    try:
        planner = TravelPlannerV2(
            provider=provider,
            model=model,
            verbose=True,
            enable_monitoring=enable_monitoring
        )
        st.session_state.planner = planner
        return True, "✅ Planner initialized successfully!"
    except Exception as e:
        return False, f"❌ Failed to initialize planner: {str(e)}"


def update_context_from_state(state: TravelPlannerState):
    """Update conversation context from workflow state."""
    context = st.session_state.conversation_context

    # Update with new information from state
    if state.get("origin"):
        context["origin"] = state["origin"]
    if state.get("destination"):
        context["destination"] = state["destination"]
    if state.get("departure_date"):
        context["departure_date"] = state["departure_date"]
    if state.get("return_date"):
        context["return_date"] = state["return_date"]
    if state.get("num_passengers"):
        context["num_passengers"] = state["num_passengers"]
    if state.get("budget"):
        context["budget"] = state["budget"]

    # Store last state for reference
    context["last_state"] = state


async def process_message(user_message: str) -> Dict[str, Any]:
    """
    Process user message with context preservation.

    Args:
        user_message: User's message

    Returns:
        Dictionary with response and metadata
    """
    planner = st.session_state.planner
    context = st.session_state.conversation_context

    if planner is None:
        return {
            "response": "❌ Planner not initialized. Please configure settings in the sidebar.",
            "error": True
        }

    try:
        # Use context from previous conversation
        result: TravelPlannerState = await planner.plan_trip(
            query=user_message,
            origin=context.get("origin"),
            destination=context.get("destination"),
            departure_date=context.get("departure_date"),
            return_date=context.get("return_date"),
            num_passengers=context.get("num_passengers", 1),
            budget=context.get("budget"),
            preferences=context.get("preferences", {})
        )

        # Update context with new information
        update_context_from_state(result)

        # Prepare response
        response_parts = []

        # Main itinerary
        if result.get("itinerary"):
            response_parts.append(result["itinerary"])

        # Flight options (if any)
        if result.get("flight_options"):
            response_parts.append(f"\n\n✈️ **Found {len(result['flight_options'])} flight options**")

        # Hotel options (if any)
        if result.get("hotel_options"):
            response_parts.append(f"\n\n🏨 **Found {len(result['hotel_options'])} hotel options**")

        # Activity options (if any)
        if result.get("activity_options"):
            response_parts.append(f"\n\n🎭 **Found {len(result['activity_options'])} activity options**")

        # Recommendations
        if result.get("recommendations"):
            response_parts.append("\n\n📋 **Recommendations:**")
            for rec in result["recommendations"]:
                response_parts.append(f"- {rec}")

        # Errors (if any)
        if result.get("errors"):
            response_parts.append("\n\n⚠️ **Warnings:**")
            for error in result["errors"]:
                response_parts.append(f"- {error}")

        response = "\n".join(response_parts) if response_parts else "I couldn't generate a response. Please try rephrasing your request."

        return {
            "response": response,
            "metadata": {
                "completed_steps": result.get("completed_steps", []),
                "total_cost": result.get("total_cost", 0.0),
                "flight_count": len(result.get("flight_options", [])),
                "hotel_count": len(result.get("hotel_options", [])),
                "activity_count": len(result.get("activity_options", [])),
            },
            "state": result,
            "error": False
        }

    except Exception as e:
        return {
            "response": f"❌ Error processing your request: {str(e)}",
            "error": True
        }


def display_message(role: str, content: str, metadata: Dict[str, Any] = None):
    """Display a chat message with metadata."""
    with st.chat_message(role):
        st.markdown(content)

        if metadata and role == "assistant":
            with st.expander("📊 Details", expanded=False):
                col1, col2, col3, col4 = st.columns(4)

                with col1:
                    st.metric("✈️ Flights", metadata.get("flight_count", 0))
                with col2:
                    st.metric("🏨 Hotels", metadata.get("hotel_count", 0))
                with col3:
                    st.metric("🎭 Activities", metadata.get("activity_count", 0))
                with col4:
                    cost = metadata.get("total_cost", 0.0)
                    st.metric("💰 Cost", f"${cost:,.0f}" if cost > 0 else "N/A")

                if metadata.get("completed_steps"):
                    st.write("**Completed Steps:**", ", ".join(metadata["completed_steps"]))


def main():
    """Main Streamlit application."""
    init_session_state()

    # Sidebar configuration
    with st.sidebar:
        st.title("⚙️ Settings")

        # Provider selection
        provider = st.selectbox(
            "LLM Provider",
            ["anthropic", "openai", "openrouter"],
            index=0,
            help="Select the LLM provider to use"
        )

        # Model selection (optional)
        model = st.text_input(
            "Model (optional)",
            placeholder="Leave empty for default",
            help="Specify a custom model name"
        )

        # Monitoring toggle
        enable_monitoring = st.checkbox(
            "Enable LangSmith Monitoring",
            value=True,
            help="Trace workflow execution in LangSmith (requires LANGCHAIN_TRACING_V2=true in .env)"
        )

        # Initialize button
        if st.button("🚀 Initialize Planner", type="primary"):
            with st.spinner("Initializing..."):
                success, message = initialize_planner(
                    provider=provider,
                    model=model if model else None,
                    enable_monitoring=enable_monitoring
                )
                if success:
                    st.success(message)
                else:
                    st.error(message)

        st.divider()

        # Current context display
        st.subheader("💬 Conversation Context")
        context = st.session_state.conversation_context

        if context.get("origin"):
            st.text(f"📍 Origin: {context['origin']}")
        if context.get("destination"):
            st.text(f"📍 Destination: {context['destination']}")
        if context.get("departure_date"):
            st.text(f"📅 Departure: {context['departure_date']}")
        if context.get("return_date"):
            st.text(f"📅 Return: {context['return_date']}")
        if context.get("num_passengers"):
            st.text(f"👥 Passengers: {context['num_passengers']}")
        if context.get("budget"):
            st.text(f"💰 Budget: ${context['budget']:,.0f}")

        # Clear context button
        if st.button("🗑️ Clear Context"):
            st.session_state.conversation_context = {
                "origin": None,
                "destination": None,
                "departure_date": None,
                "return_date": None,
                "num_passengers": 1,
                "budget": None,
                "preferences": {},
                "last_state": None
            }
            st.rerun()

        # Clear conversation button
        if st.button("🔄 New Conversation"):
            st.session_state.messages = []
            st.session_state.conversation_context = {
                "origin": None,
                "destination": None,
                "departure_date": None,
                "return_date": None,
                "num_passengers": 1,
                "budget": None,
                "preferences": {},
                "last_state": None
            }
            st.session_state.conversation_id = datetime.now().strftime("%Y%m%d_%H%M%S")
            st.rerun()

        st.divider()

        # Info
        st.caption(f"Conversation ID: {st.session_state.conversation_id}")
        st.caption(f"Messages: {len(st.session_state.messages)}")

    # Main chat interface
    st.title("✈️ Travel Planner V2 - Chat Interface")
    st.caption("Powered by LangGraph with context preservation")

    # Display chat messages
    for message in st.session_state.messages:
        display_message(
            message["role"],
            message["content"],
            message.get("metadata")
        )

    # Chat input
    if prompt := st.chat_input("Ask me about your travel plans..."):
        # Check if planner is initialized
        if st.session_state.planner is None:
            st.error("⚠️ Please initialize the planner first using the sidebar settings.")
            return

        # Add user message to history
        st.session_state.messages.append({
            "role": "user",
            "content": prompt,
            "timestamp": datetime.now().isoformat()
        })

        # Display user message
        display_message("user", prompt)

        # Process message and get response
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                # Run async function
                result = asyncio.run(process_message(prompt))

                if result["error"]:
                    st.error(result["response"])
                else:
                    st.markdown(result["response"])

                    # Display metadata
                    if result.get("metadata"):
                        with st.expander("📊 Details", expanded=False):
                            col1, col2, col3, col4 = st.columns(4)

                            metadata = result["metadata"]
                            with col1:
                                st.metric("✈️ Flights", metadata.get("flight_count", 0))
                            with col2:
                                st.metric("🏨 Hotels", metadata.get("hotel_count", 0))
                            with col3:
                                st.metric("🎭 Activities", metadata.get("activity_count", 0))
                            with col4:
                                cost = metadata.get("total_cost", 0.0)
                                st.metric("💰 Cost", f"${cost:,.0f}" if cost > 0 else "N/A")

                            if metadata.get("completed_steps"):
                                st.write("**Completed Steps:**", ", ".join(metadata["completed_steps"]))

        # Add assistant message to history
        st.session_state.messages.append({
            "role": "assistant",
            "content": result["response"],
            "metadata": result.get("metadata"),
            "timestamp": datetime.now().isoformat()
        })


if __name__ == "__main__":
    main()

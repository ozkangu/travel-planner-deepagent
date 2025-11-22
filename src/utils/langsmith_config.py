"""LangSmith configuration and setup for observability."""

import os
from typing import Optional
from dotenv import load_dotenv


def setup_langsmith(
    project_name: str = "travel-planner-deepagent",
    enabled: Optional[bool] = None
) -> bool:
    """
    Set up LangSmith for agent observability and tracing.

    LangSmith provides:
    - Detailed trace visualization of agent execution
    - Token usage tracking
    - Latency monitoring
    - Error tracking
    - Cost estimation
    - Comparison between runs

    Args:
        project_name: Name of the LangSmith project
        enabled: Whether to enable LangSmith (None = auto-detect from env)

    Returns:
        True if LangSmith is enabled, False otherwise

    Environment Variables:
        LANGCHAIN_TRACING_V2: Set to 'true' to enable tracing
        LANGCHAIN_API_KEY: Your LangSmith API key
        LANGCHAIN_PROJECT: Project name (optional, defaults to parameter)
        LANGCHAIN_ENDPOINT: LangSmith endpoint (optional)
    """

    load_dotenv()

    # Auto-detect if not specified
    if enabled is None:
        enabled = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"

    # Check for API key
    api_key = os.getenv("LANGCHAIN_API_KEY")

    if enabled and not api_key:
        print("⚠️  WARNING: LANGCHAIN_TRACING_V2 is enabled but LANGCHAIN_API_KEY is not set")
        print("   LangSmith tracing will not work. Get your API key at: https://smith.langchain.com/")
        return False

    if enabled:
        # Set environment variables
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_PROJECT"] = os.getenv("LANGCHAIN_PROJECT", project_name)

        # Optional: Set endpoint if provided
        endpoint = os.getenv("LANGCHAIN_ENDPOINT")
        if endpoint:
            os.environ["LANGCHAIN_ENDPOINT"] = endpoint

        print(f"✅ LangSmith tracing enabled for project: {os.environ['LANGCHAIN_PROJECT']}")
        print(f"   View traces at: https://smith.langchain.com/")
        return True
    else:
        os.environ["LANGCHAIN_TRACING_V2"] = "false"
        return False


def get_langsmith_url(run_id: str) -> str:
    """
    Get the LangSmith URL for a specific run.

    Args:
        run_id: The run ID from LangChain

    Returns:
        URL to view the run in LangSmith
    """
    return f"https://smith.langchain.com/public/{run_id}/r"


def print_langsmith_instructions():
    """Print instructions for setting up LangSmith."""

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║                       LANGSMITH SETUP INSTRUCTIONS                           ║
╚══════════════════════════════════════════════════════════════════════════════╝

LangSmith is LangChain's official observability platform. It provides:
  ✅ Visual trace of agent execution flow
  ✅ Token usage and cost tracking
  ✅ Latency monitoring
  ✅ Error tracking and debugging
  ✅ Run comparisons and analytics

SETUP STEPS:

1️⃣  Get your LangSmith API key:
   - Visit: https://smith.langchain.com/
   - Sign up or log in
   - Go to Settings → API Keys
   - Create a new API key

2️⃣  Add to your .env file:
   LANGCHAIN_TRACING_V2=true
   LANGCHAIN_API_KEY=your_api_key_here
   LANGCHAIN_PROJECT=travel-planner-deepagent

3️⃣  Run your agent normally:
   python demo.py interactive

4️⃣  View traces in LangSmith:
   - Go to https://smith.langchain.com/
   - Select your project
   - View detailed traces of each agent execution

WHAT YOU'LL SEE IN LANGSMITH:

📊 Agent Execution Flow:
   - Each agent call visualized as a node
   - Tool calls and their inputs/outputs
   - LLM calls with full prompts and responses

💰 Token & Cost Tracking:
   - Token usage per agent
   - Token usage per LLM call
   - Estimated costs

⏱️  Performance Metrics:
   - Total execution time
   - Time per agent
   - Time per LLM call
   - Time per tool call

🐛 Debugging:
   - Full error traces
   - Input/output at each step
   - Intermediate states

📈 Analytics:
   - Compare runs
   - Track performance over time
   - Identify bottlenecks

════════════════════════════════════════════════════════════════════════════════
""")


if __name__ == "__main__":
    print_langsmith_instructions()

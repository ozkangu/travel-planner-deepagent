"""Demo script for Travel Planner with Monitoring."""

import os
from dotenv import load_dotenv
from src.travel_planner_monitored import create_monitored_travel_planner
from src.utils.langsmith_config import print_langsmith_instructions


def simple_monitored_demo():
    """Run a simple demo with monitoring enabled."""

    print("=" * 80)
    print("TRAVEL PLANNER WITH MONITORING - SIMPLE DEMO")
    print("=" * 80)
    print()

    # Load environment variables
    load_dotenv()

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("⚠️  ERROR: No API key found!")
        print("Please set ANTHROPIC_API_KEY or OPENAI_API_KEY in your .env file")
        return

    # Check for LangSmith
    langsmith_enabled = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"
    if langsmith_enabled and not os.getenv("LANGCHAIN_API_KEY"):
        print("⚠️  WARNING: LANGCHAIN_TRACING_V2=true but LANGCHAIN_API_KEY not set")
        print("LangSmith tracing will be disabled.")
        langsmith_enabled = False

    # Create the monitored travel planner
    print("🚀 Initializing Monitored Travel Planner Agent...")
    provider = "anthropic" if os.getenv("ANTHROPIC_API_KEY") else "openai"

    planner = create_monitored_travel_planner(
        provider=provider,
        enable_monitoring=True,
        enable_langsmith=langsmith_enabled,
        log_level="INFO"
    )

    print(f"✅ Agent initialized with {provider} provider")
    print(f"📊 Monitoring: Enabled")
    print(f"📈 LangSmith: {'Enabled' if langsmith_enabled else 'Disabled'}")
    print()

    # Example query
    query = "I want to fly from Istanbul to London on December 20th, returning December 27th. Find me some flight options."

    print(f"{'=' * 80}")
    print(f"Example Query:")
    print(f"{'=' * 80}")
    print(f"👤 User: {query}")
    print()
    print("🤖 Agent: Processing your request...")
    print("-" * 80)

    try:
        # Invoke with metrics
        result = planner.invoke(query, print_metrics=True)

        # Display response
        print("\n" + "=" * 80)
        print("RESPONSE:")
        print("=" * 80)
        for msg in result["messages"]:
            if hasattr(msg, 'content') and msg.type in ["human", "ai"]:
                role = "👤 User" if msg.type == "human" else "🤖 Agent"
                if not hasattr(msg, 'tool_calls'):
                    print(f"{role}: {msg.content}")
                    print()

        # Save metrics
        planner.save_metrics("logs/metrics_latest.json")

        # Additional metrics summary
        if "metrics" in result:
            print("\n" + "=" * 80)
            print("📊 QUICK METRICS SUMMARY")
            print("=" * 80)
            totals = result["metrics"]["totals"]
            print(f"Total Tokens: {totals['total_tokens']:,}")
            print(f"Total Cost: ${totals['estimated_cost']:.6f}")
            print(f"LLM Calls: {totals['llm_calls']}")
            print(f"Tool Calls: {totals['tool_calls']}")
            print("=" * 80)

    except Exception as e:
        print(f"❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()

    print("\n✅ Demo completed!")


def interactive_monitored_demo():
    """Run an interactive demo with monitoring."""

    print("=" * 80)
    print("TRAVEL PLANNER WITH MONITORING - INTERACTIVE DEMO")
    print("=" * 80)
    print()

    # Load environment variables
    load_dotenv()

    # Check for API key
    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("⚠️  ERROR: No API key found!")
        return

    # Check for LangSmith
    langsmith_enabled = os.getenv("LANGCHAIN_TRACING_V2", "false").lower() == "true"

    # Create planner
    print("🚀 Initializing Monitored Travel Planner Agent...")
    provider = "anthropic" if os.getenv("ANTHROPIC_API_KEY") else "openai"

    planner = create_monitored_travel_planner(
        provider=provider,
        enable_monitoring=True,
        enable_langsmith=langsmith_enabled,
        log_level="INFO"
    )

    print(f"✅ Agent initialized")
    print(f"📊 Monitoring: Enabled")
    print(f"📈 LangSmith: {'Enabled - View at https://smith.langchain.com/' if langsmith_enabled else 'Disabled'}")
    print()

    print("💡 Tips:")
    print("  - Type 'metrics' to see current session metrics")
    print("  - Type 'save' to save metrics to file")
    print("  - Type 'reset' to reset metrics")
    print("  - Type 'langsmith' for LangSmith setup instructions")
    print("  - Type 'exit' or 'quit' to end")
    print()

    session_count = 0

    while True:
        print("-" * 80)
        user_input = input("👤 You: ").strip()
        print()

        if not user_input:
            continue

        if user_input.lower() in ['exit', 'quit', 'bye']:
            print("👋 Thanks for using Travel Planner!")
            # Print final metrics
            print("\n" + "=" * 80)
            print("FINAL SESSION METRICS")
            print("=" * 80)
            planner.metrics_callback.print_summary()
            break

        if user_input.lower() == 'metrics':
            planner.metrics_callback.print_summary()
            continue

        if user_input.lower() == 'save':
            filename = f"logs/metrics_session_{session_count}.json"
            planner.save_metrics(filename)
            print(f"✅ Metrics saved to {filename}")
            continue

        if user_input.lower() == 'reset':
            planner.reset_metrics()
            print("✅ Metrics reset")
            session_count += 1
            continue

        if user_input.lower() == 'langsmith':
            print_langsmith_instructions()
            continue

        try:
            print("🤖 Agent: Processing your request...")
            print()

            result = planner.invoke(user_input, print_metrics=False)

            # Get latest response
            for msg in reversed(result["messages"]):
                if msg.type == "ai" and not hasattr(msg, 'tool_calls'):
                    print(f"🤖 Agent: {msg.content}")
                    print()
                    break

        except Exception as e:
            print(f"❌ Error: {str(e)}")
            print()


def comparison_demo():
    """Run comparison between different queries to show metrics."""

    print("=" * 80)
    print("AGENT PERFORMANCE COMPARISON DEMO")
    print("=" * 80)
    print()

    load_dotenv()

    if not os.getenv("ANTHROPIC_API_KEY") and not os.getenv("OPENAI_API_KEY"):
        print("⚠️  ERROR: No API key found!")
        return

    provider = "anthropic" if os.getenv("ANTHROPIC_API_KEY") else "openai"

    # Different queries to compare
    queries = [
        {
            "name": "Simple Flight Search",
            "query": "Find flights from Istanbul to London on December 20th"
        },
        {
            "name": "Complex Trip Planning",
            "query": "Plan a 5-day trip to Paris including flights from New York, hotel, and activities"
        },
        {
            "name": "Weather Only",
            "query": "What's the weather in London in December?"
        },
        {
            "name": "Activity Search",
            "query": "Recommend activities in Istanbul for 3 days"
        }
    ]

    results = []

    for test in queries:
        print(f"\n{'=' * 80}")
        print(f"Testing: {test['name']}")
        print(f"{'=' * 80}")

        planner = create_monitored_travel_planner(
            provider=provider,
            enable_monitoring=True,
            enable_langsmith=False,
            log_level="WARNING"  # Less verbose
        )

        result = planner.invoke(test['query'], print_metrics=False)

        if "metrics" in result:
            metrics = result["metrics"]
            results.append({
                "name": test['name'],
                "duration": metrics['session_duration'],
                "tokens": metrics['totals']['total_tokens'],
                "cost": metrics['totals']['estimated_cost'],
                "llm_calls": metrics['totals']['llm_calls'],
                "tool_calls": metrics['totals']['tool_calls']
            })

            print(f"✅ Completed in {metrics['session_duration']:.2f}s")
            print(f"   Tokens: {metrics['totals']['total_tokens']:,}")
            print(f"   Cost: ${metrics['totals']['estimated_cost']:.6f}")

    # Print comparison table
    print("\n" + "=" * 80)
    print("PERFORMANCE COMPARISON")
    print("=" * 80)
    print()
    print(f"{'Query':<30} {'Duration':<12} {'Tokens':<12} {'Cost':<12} {'LLM':<8} {'Tools':<8}")
    print("-" * 80)

    for r in results:
        print(f"{r['name']:<30} {r['duration']:<12.2f} {r['tokens']:<12,} ${r['cost']:<11.6f} {r['llm_calls']:<8} {r['tool_calls']:<8}")

    print("=" * 80)


if __name__ == "__main__":
    import sys

    print("""
╔══════════════════════════════════════════════════════════════════════════════╗
║              TRAVEL PLANNER WITH MONITORING & OBSERVABILITY                  ║
║                                                                              ║
║  Track token usage, execution time, costs, and agent performance            ║
╚══════════════════════════════════════════════════════════════════════════════╝
""")

    if len(sys.argv) > 1:
        mode = sys.argv[1].lower()
    else:
        print("Select demo mode:")
        print("  1. Simple Demo (single query with full metrics)")
        print("  2. Interactive Demo (chat with metrics)")
        print("  3. Comparison Demo (compare different queries)")
        print("  4. LangSmith Setup Instructions")
        print()
        choice = input("Enter your choice (1-4): ").strip()

        mode_map = {
            "1": "simple",
            "2": "interactive",
            "3": "comparison",
            "4": "langsmith"
        }
        mode = mode_map.get(choice, "simple")

    print()

    if mode == "interactive":
        interactive_monitored_demo()
    elif mode == "comparison":
        comparison_demo()
    elif mode == "langsmith":
        print_langsmith_instructions()
    else:
        simple_monitored_demo()

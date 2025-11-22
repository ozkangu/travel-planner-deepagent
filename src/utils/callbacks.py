"""Custom callbacks for monitoring agent performance."""

from typing import Any, Dict, List, Optional
from datetime import datetime
import time
from langchain_core.callbacks import BaseCallbackHandler
from langchain_core.outputs import LLMResult
from langchain_core.messages import BaseMessage
import json


class AgentMetricsCallback(BaseCallbackHandler):
    """
    Custom callback handler to track agent performance metrics.

    Tracks:
    - Token usage (prompt, completion, total)
    - Execution time
    - Cost estimation
    - Tool calls
    - Errors
    """

    def __init__(self, agent_name: str = "unknown"):
        """
        Initialize the metrics callback.

        Args:
            agent_name: Name of the agent being tracked
        """
        super().__init__()
        self.agent_name = agent_name
        self.metrics = {
            "agent_name": agent_name,
            "start_time": None,
            "end_time": None,
            "duration_seconds": 0,
            "llm_calls": 0,
            "tool_calls": 0,
            "tokens": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            },
            "estimated_cost": 0.0,
            "errors": [],
            "tool_usage": {},
            "llm_timings": []
        }
        self.llm_start_times = {}

        # Pricing (as of 2024 - update as needed)
        self.pricing = {
            "claude-3-5-sonnet-20241022": {
                "input": 0.003,   # per 1K tokens
                "output": 0.015   # per 1K tokens
            },
            "gpt-4-turbo-preview": {
                "input": 0.01,
                "output": 0.03
            },
            "gpt-4": {
                "input": 0.03,
                "output": 0.06
            },
            "gpt-3.5-turbo": {
                "input": 0.0005,
                "output": 0.0015
            }
        }

    def on_chain_start(
        self,
        serialized: Dict[str, Any],
        inputs: Dict[str, Any],
        **kwargs: Any
    ) -> None:
        """Run when chain starts."""
        if self.metrics["start_time"] is None:
            self.metrics["start_time"] = datetime.now()

    def on_chain_end(self, outputs: Dict[str, Any], **kwargs: Any) -> None:
        """Run when chain ends."""
        if self.metrics["end_time"] is None:
            self.metrics["end_time"] = datetime.now()
            if self.metrics["start_time"]:
                duration = (self.metrics["end_time"] - self.metrics["start_time"]).total_seconds()
                self.metrics["duration_seconds"] = round(duration, 3)

    def on_llm_start(
        self,
        serialized: Dict[str, Any],
        prompts: List[str],
        **kwargs: Any
    ) -> None:
        """Run when LLM starts."""
        run_id = kwargs.get("run_id", str(time.time()))
        self.llm_start_times[run_id] = time.time()
        self.metrics["llm_calls"] += 1

    def on_llm_end(self, response: LLMResult, **kwargs: Any) -> None:
        """Run when LLM ends."""
        run_id = kwargs.get("run_id", None)

        # Track timing
        if run_id and run_id in self.llm_start_times:
            duration = time.time() - self.llm_start_times[run_id]
            self.metrics["llm_timings"].append(round(duration, 3))
            del self.llm_start_times[run_id]

        # Track token usage
        if response.llm_output:
            token_usage = response.llm_output.get("token_usage", {})

            prompt_tokens = token_usage.get("prompt_tokens", 0)
            completion_tokens = token_usage.get("completion_tokens", 0)
            total_tokens = token_usage.get("total_tokens", 0)

            self.metrics["tokens"]["prompt_tokens"] += prompt_tokens
            self.metrics["tokens"]["completion_tokens"] += completion_tokens
            self.metrics["tokens"]["total_tokens"] += total_tokens

            # Estimate cost
            model_name = response.llm_output.get("model_name", "")
            cost = self._calculate_cost(model_name, prompt_tokens, completion_tokens)
            self.metrics["estimated_cost"] += cost

    def on_tool_start(
        self,
        serialized: Dict[str, Any],
        input_str: str,
        **kwargs: Any,
    ) -> None:
        """Run when tool starts."""
        self.metrics["tool_calls"] += 1

        # Track individual tool usage
        tool_name = serialized.get("name", "unknown_tool")
        if tool_name not in self.metrics["tool_usage"]:
            self.metrics["tool_usage"][tool_name] = 0
        self.metrics["tool_usage"][tool_name] += 1

    def on_tool_error(
        self, error: Exception, **kwargs: Any
    ) -> None:
        """Run when tool errors."""
        self.metrics["errors"].append({
            "type": "tool_error",
            "error": str(error),
            "timestamp": datetime.now().isoformat()
        })

    def on_llm_error(
        self, error: Exception, **kwargs: Any
    ) -> None:
        """Run when LLM errors."""
        self.metrics["errors"].append({
            "type": "llm_error",
            "error": str(error),
            "timestamp": datetime.now().isoformat()
        })

    def on_chain_error(
        self, error: Exception, **kwargs: Any
    ) -> None:
        """Run when chain errors."""
        self.metrics["errors"].append({
            "type": "chain_error",
            "error": str(error),
            "timestamp": datetime.now().isoformat()
        })

    def _calculate_cost(self, model_name: str, prompt_tokens: int, completion_tokens: int) -> float:
        """Calculate estimated cost based on token usage."""
        # Find matching pricing
        pricing = None
        for model_key, model_pricing in self.pricing.items():
            if model_key in model_name.lower():
                pricing = model_pricing
                break

        if not pricing:
            return 0.0

        # Calculate cost
        prompt_cost = (prompt_tokens / 1000) * pricing["input"]
        completion_cost = (completion_tokens / 1000) * pricing["output"]

        return round(prompt_cost + completion_cost, 6)

    def get_metrics(self) -> Dict[str, Any]:
        """Get the collected metrics."""
        # Add calculated fields
        metrics = self.metrics.copy()

        # Average LLM timing
        if metrics["llm_timings"]:
            metrics["avg_llm_duration"] = round(
                sum(metrics["llm_timings"]) / len(metrics["llm_timings"]),
                3
            )
        else:
            metrics["avg_llm_duration"] = 0

        return metrics

    def reset(self):
        """Reset metrics for a new run."""
        self.__init__(self.agent_name)

    def print_summary(self):
        """Print a formatted summary of metrics."""
        metrics = self.get_metrics()

        print("\n" + "=" * 80)
        print(f"📊 AGENT METRICS: {self.agent_name.upper()}")
        print("=" * 80)

        # Timing
        print(f"\n⏱️  TIMING:")
        print(f"  Duration: {metrics['duration_seconds']:.3f}s")
        if metrics['llm_timings']:
            print(f"  Avg LLM Call: {metrics['avg_llm_duration']:.3f}s")
            print(f"  LLM Calls: {metrics['llm_calls']}")

        # Tokens
        print(f"\n🎯 TOKEN USAGE:")
        print(f"  Prompt Tokens: {metrics['tokens']['prompt_tokens']:,}")
        print(f"  Completion Tokens: {metrics['tokens']['completion_tokens']:,}")
        print(f"  Total Tokens: {metrics['tokens']['total_tokens']:,}")

        # Cost
        print(f"\n💰 ESTIMATED COST:")
        print(f"  ${metrics['estimated_cost']:.6f}")

        # Tools
        if metrics['tool_calls'] > 0:
            print(f"\n🔧 TOOL USAGE:")
            print(f"  Total Tool Calls: {metrics['tool_calls']}")
            for tool_name, count in metrics['tool_usage'].items():
                print(f"    - {tool_name}: {count}")

        # Errors
        if metrics['errors']:
            print(f"\n❌ ERRORS ({len(metrics['errors'])}):")
            for error in metrics['errors']:
                print(f"    - {error['type']}: {error['error'][:80]}")

        print("=" * 80 + "\n")


class MultiAgentMetricsCallback(BaseCallbackHandler):
    """
    Callback handler to track metrics across multiple agents.
    Aggregates metrics from all agents in the system.
    """

    def __init__(self):
        """Initialize the multi-agent metrics callback."""
        super().__init__()
        self.agent_metrics = {}
        self.current_agent = None
        self.session_start = datetime.now()

    def set_current_agent(self, agent_name: str):
        """Set the current agent being tracked."""
        self.current_agent = agent_name
        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = AgentMetricsCallback(agent_name)

    def get_agent_callback(self, agent_name: str) -> AgentMetricsCallback:
        """Get or create callback for a specific agent."""
        if agent_name not in self.agent_metrics:
            self.agent_metrics[agent_name] = AgentMetricsCallback(agent_name)
        return self.agent_metrics[agent_name]

    def get_all_metrics(self) -> Dict[str, Any]:
        """Get aggregated metrics from all agents."""
        all_metrics = {
            "session_start": self.session_start.isoformat(),
            "session_duration": (datetime.now() - self.session_start).total_seconds(),
            "agents": {},
            "totals": {
                "llm_calls": 0,
                "tool_calls": 0,
                "total_tokens": 0,
                "estimated_cost": 0.0,
                "errors": 0
            }
        }

        for agent_name, callback in self.agent_metrics.items():
            metrics = callback.get_metrics()
            all_metrics["agents"][agent_name] = metrics

            # Aggregate totals
            all_metrics["totals"]["llm_calls"] += metrics["llm_calls"]
            all_metrics["totals"]["tool_calls"] += metrics["tool_calls"]
            all_metrics["totals"]["total_tokens"] += metrics["tokens"]["total_tokens"]
            all_metrics["totals"]["estimated_cost"] += metrics["estimated_cost"]
            all_metrics["totals"]["errors"] += len(metrics["errors"])

        return all_metrics

    def print_summary(self):
        """Print a comprehensive summary of all agent metrics."""
        all_metrics = self.get_all_metrics()

        print("\n" + "=" * 80)
        print("📊 MULTI-AGENT SESSION SUMMARY")
        print("=" * 80)

        print(f"\n⏱️  SESSION DURATION: {all_metrics['session_duration']:.2f}s")

        print(f"\n📈 TOTALS ACROSS ALL AGENTS:")
        print(f"  Total LLM Calls: {all_metrics['totals']['llm_calls']}")
        print(f"  Total Tool Calls: {all_metrics['totals']['tool_calls']}")
        print(f"  Total Tokens: {all_metrics['totals']['total_tokens']:,}")
        print(f"  Total Cost: ${all_metrics['totals']['estimated_cost']:.6f}")
        if all_metrics['totals']['errors'] > 0:
            print(f"  Total Errors: {all_metrics['totals']['errors']}")

        print(f"\n🤖 PER-AGENT BREAKDOWN:")
        for agent_name, metrics in all_metrics['agents'].items():
            if metrics['llm_calls'] > 0 or metrics['tool_calls'] > 0:
                print(f"\n  {agent_name.upper()}:")
                print(f"    Duration: {metrics['duration_seconds']:.3f}s")
                print(f"    Tokens: {metrics['tokens']['total_tokens']:,}")
                print(f"    Cost: ${metrics['estimated_cost']:.6f}")
                print(f"    LLM Calls: {metrics['llm_calls']}, Tool Calls: {metrics['tool_calls']}")

        print("\n" + "=" * 80 + "\n")

    def save_metrics(self, filepath: str):
        """Save metrics to a JSON file."""
        metrics = self.get_all_metrics()
        with open(filepath, 'w') as f:
            json.dump(metrics, f, indent=2)
        print(f"✅ Metrics saved to {filepath}")

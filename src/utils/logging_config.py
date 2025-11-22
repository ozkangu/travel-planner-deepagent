"""Logging configuration for the travel planner."""

import logging
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional


class ColoredFormatter(logging.Formatter):
    """Custom formatter with colors for console output."""

    # ANSI color codes
    COLORS = {
        'DEBUG': '\033[36m',      # Cyan
        'INFO': '\033[32m',       # Green
        'WARNING': '\033[33m',    # Yellow
        'ERROR': '\033[31m',      # Red
        'CRITICAL': '\033[35m',   # Magenta
        'RESET': '\033[0m'        # Reset
    }

    def format(self, record):
        """Format the log record with colors."""
        # Add color to level name
        levelname = record.levelname
        if levelname in self.COLORS:
            record.levelname = f"{self.COLORS[levelname]}{levelname}{self.COLORS['RESET']}"

        # Add color to agent name if present
        if hasattr(record, 'agent_name'):
            record.agent_name = f"\033[1m{record.agent_name}\033[0m"  # Bold

        return super().format(record)


def setup_logging(
    log_level: str = "INFO",
    log_to_file: bool = True,
    log_dir: str = "logs",
    console_output: bool = True
) -> logging.Logger:
    """
    Set up logging configuration for the travel planner.

    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_to_file: Whether to log to file
        log_dir: Directory for log files
        console_output: Whether to output to console

    Returns:
        Configured logger instance
    """

    # Create logger
    logger = logging.getLogger("travel_planner")
    logger.setLevel(getattr(logging, log_level.upper()))

    # Remove existing handlers
    logger.handlers = []

    # Create formatters
    detailed_formatter = logging.Formatter(
        '%(asctime)s | %(levelname)-8s | %(name)s | %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    colored_formatter = ColoredFormatter(
        '%(asctime)s | %(levelname)-8s | %(message)s',
        datefmt='%H:%M:%S'
    )

    # Console handler
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(getattr(logging, log_level.upper()))
        console_handler.setFormatter(colored_formatter)
        logger.addHandler(console_handler)

    # File handler
    if log_to_file:
        # Create logs directory
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True)

        # Create log file with timestamp
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        log_file = log_path / f"travel_planner_{timestamp}.log"

        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(logging.DEBUG)  # File gets all logs
        file_handler.setFormatter(detailed_formatter)
        logger.addHandler(file_handler)

        logger.info(f"Logging to file: {log_file}")

    return logger


def get_agent_logger(agent_name: str) -> logging.Logger:
    """
    Get a logger for a specific agent.

    Args:
        agent_name: Name of the agent

    Returns:
        Logger instance for the agent
    """
    logger = logging.getLogger(f"travel_planner.{agent_name}")
    return logger


class AgentLogAdapter(logging.LoggerAdapter):
    """
    Logger adapter that adds agent name to all log messages.
    """

    def process(self, msg, kwargs):
        """Add agent name to the log message."""
        agent_name = self.extra.get('agent_name', 'unknown')
        return f"[{agent_name}] {msg}", kwargs


def log_agent_start(logger: logging.Logger, agent_name: str, task: str):
    """Log agent start."""
    logger.info(f"🚀 {agent_name} starting task: {task}")


def log_agent_end(logger: logging.Logger, agent_name: str, duration: float):
    """Log agent completion."""
    logger.info(f"✅ {agent_name} completed in {duration:.3f}s")


def log_tool_call(logger: logging.Logger, tool_name: str, args: dict):
    """Log tool invocation."""
    logger.debug(f"🔧 Calling tool: {tool_name} with args: {args}")


def log_llm_call(logger: logging.Logger, agent_name: str, prompt_length: int):
    """Log LLM call."""
    logger.debug(f"🤖 {agent_name} calling LLM (prompt length: {prompt_length})")


def log_error(logger: logging.Logger, agent_name: str, error: Exception):
    """Log error."""
    logger.error(f"❌ {agent_name} error: {str(error)}", exc_info=True)

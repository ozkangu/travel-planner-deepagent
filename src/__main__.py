"""
Main entry point for running the Travel Planner as a module.

Usage:
    python -m src
"""

import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from demo import interactive_demo

if __name__ == "__main__":
    interactive_demo()

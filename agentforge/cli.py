"""CLI: python -m agentforge.cli "your task" [--agent coder] [--max-steps 4]"""
from __future__ import annotations

import argparse
import json
import sys

from dotenv import load_dotenv

from .agents import AGENTS, get_agent
from .router import route_task

load_dotenv()


def main() -> int:
    parser = argparse.ArgumentParser(description="AgentForge CLI")
    parser.add_argument("task", help="Task description")
    parser.add_argument(
        "--agent",
        choices=list(AGENTS) + ["route"],
        default="route",
        help="Specific agent to invoke, or 'route' to let the router plan.",
    )
    parser.add_argument("--max-steps", type=int, default=4)
    args = parser.parse_args()

    if args.agent == "route":
        result = route_task(args.task, max_steps=args.max_steps)
        print(result["final"])
        print("\n--- trace ---")
        print(json.dumps(result["trace"], indent=2))
    else:
        print(get_agent(args.agent).invoke(args.task))
    return 0


if __name__ == "__main__":
    sys.exit(main())

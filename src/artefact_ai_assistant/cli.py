"""Command-line interface for the assistant.

Usage: artefact-ai-assistant "your question here" [--verbose]
"""

import argparse

from dotenv import load_dotenv

from artefact_ai_assistant.agent import build_agent


def main() -> None:
    parser = argparse.ArgumentParser(
        prog="artefact-ai-assistant",
        description="Ask a question. The assistant decides whether to answer directly or use a tool (calculator, currency converter).",
    )
    parser.add_argument(
        "question",
        help="The question to ask. Wrap in quotes if it contains spaces.",
    )
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Print the agent's intermediate steps (tool calls and results).",
    )
    args = parser.parse_args()

    load_dotenv()
    agent = build_agent()
    result = agent.invoke({"messages": [("user", args.question)]})

    if args.verbose:
        _print_steps(result["messages"])
    else:
        print(result["messages"][-1].content)


def _print_steps(messages) -> None:
    """Pretty-print the full message sequence including tool calls."""
    for msg in messages:
        cls = type(msg).__name__
        if hasattr(msg, "tool_calls") and msg.tool_calls:
            for tc in msg.tool_calls:
                print(f"  → [{cls}] calling {tc['name']}({tc['args']})")
        else:
            content = getattr(msg, "content", "")
            if content:
                print(f"  [{cls}] {content}")
        print()
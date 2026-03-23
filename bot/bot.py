"""Telegram bot entry point.

Supports two modes:
1. --test mode: Calls handlers directly, prints to stdout, exits
2. Normal mode: Runs Telegram bot using aiogram

Usage:
    uv run bot.py --test "/start"    # Test mode
    uv run bot.py                     # Telegram bot mode
"""

import argparse
import sys
from pathlib import Path

# Add bot directory to path for imports
bot_dir = Path(__file__).parent
sys.path.insert(0, str(bot_dir))

from config import load_config
from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
    route_intent,
)


def route_command(text: str) -> str:
    """Route command text to appropriate handler.

    Args:
        text: The command text (e.g., "/start", "/help", or plain text).

    Returns:
        Handler response text.
    """
    stripped = text.strip()
    
    # Check if this is a slash command
    if stripped.startswith("/"):
        # Parse command and arguments
        parts = stripped.split(maxsplit=1)
        command = parts[0].lower()
        argument = parts[1] if len(parts) > 1 else ""

        # Route to handler
        if command == "/start":
            return handle_start(text)
        elif command == "/help":
            return handle_help(text)
        elif command == "/health":
            return handle_health(text)
        elif command == "/labs":
            return handle_labs(text)
        elif command == "/scores":
            # Pass the full text to handle_scores so it can parse the argument
            return handle_scores(text)
        else:
            return f"Unknown command: {command}. Use /help to see available commands."
    else:
        # Not a slash command - route to LLM intent router
        return route_intent(text)


def run_test_mode(command: str) -> None:
    """Run bot in test mode.
    
    Calls handler directly and prints response to stdout.
    Does not connect to Telegram.
    
    Args:
        command: The command to test (e.g., "/start").
    """
    try:
        # Load config (validates env vars)
        config = load_config()
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    
    # Route command and print response
    response = route_command(command)
    print(response)
    sys.exit(0)


def run_telegram_bot() -> None:
    """Run the Telegram bot using aiogram.
    
    This will be implemented in Task 2 when we add real Telegram support.
    """
    try:
        config = load_config()
    except ValueError as e:
        print(f"Configuration error: {e}", file=sys.stderr)
        sys.exit(1)
    
    if not config["BOT_TOKEN"]:
        print("Error: BOT_TOKEN is required for Telegram bot mode", file=sys.stderr)
        print("Set BOT_TOKEN in .env.bot.secret or use --test mode", file=sys.stderr)
        sys.exit(1)
    
    # Task 2: Implement Telegram bot using aiogram
    # For now, show a placeholder message
    print("Telegram bot mode not implemented yet. Use --test mode for now.", file=sys.stderr)
    sys.exit(1)


def main() -> None:
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Telegram bot for LMS backend"
    )
    parser.add_argument(
        "--test",
        metavar="COMMAND",
        help="Test mode: run command and print response (e.g., --test '/start')"
    )
    
    args = parser.parse_args()
    
    if args.test:
        run_test_mode(args.test)
    else:
        run_telegram_bot()


if __name__ == "__main__":
    main()

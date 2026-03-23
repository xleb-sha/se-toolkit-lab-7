"""Telegram bot entry point.

Supports two modes:
1. --test mode: Calls handlers directly, prints to stdout, exits
2. Normal mode: Runs Telegram bot using aiogram with inline keyboards

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
from keyboards import get_start_keyboard, get_help_keyboard


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
    """Run the Telegram bot using aiogram with inline keyboards.

    Handles:
    - Slash commands: /start, /help, /health, /labs, /scores
    - Plain text messages: routed to LLM intent router
    - Callback queries from inline keyboard buttons
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

    # Import aiogram
    from aiogram import Bot, Dispatcher, types
    from aiogram.filters import Command, CommandStart
    from aiogram.enums import ParseMode

    # Initialize bot and dispatcher
    bot = Bot(token=config["BOT_TOKEN"])
    dp = Dispatcher()

    @dp.message(CommandStart())
    async def cmd_start(message: types.Message) -> None:
        """Handle /start command with inline keyboard."""
        text = handle_start("/start")
        keyboard = get_start_keyboard()
        await message.answer(text, reply_markup=keyboard)

    @dp.message(Command("help"))
    async def cmd_help(message: types.Message) -> None:
        """Handle /help command with inline keyboard."""
        text = handle_help("/help")
        keyboard = get_help_keyboard()
        await message.answer(text, reply_markup=keyboard)

    @dp.message(Command("health"))
    async def cmd_health(message: types.Message) -> None:
        """Handle /health command."""
        text = handle_health("/health")
        await message.answer(text)

    @dp.message(Command("labs"))
    async def cmd_labs(message: types.Message) -> None:
        """Handle /labs command."""
        text = handle_labs("/labs")
        await message.answer(text)

    @dp.message(Command("scores"))
    async def cmd_scores(message: types.Message) -> None:
        """Handle /scores command with optional lab argument."""
        args = message.text.split(maxsplit=1)
        if len(args) > 1:
            text = handle_scores(f"/scores {args[1]}")
        else:
            text = "Usage: /scores <lab> (e.g., /scores lab-04)"
        await message.answer(text)

    @dp.message()
    async def handle_message(message: types.Message) -> None:
        """Handle plain text messages via LLM intent router."""
        if message.text:
            # Use LLM for intent routing
            text = route_intent(message.text)
            await message.answer(text)

    @dp.callback_query()
    async def handle_callback(callback: types.CallbackQuery) -> None:
        """Handle inline keyboard button clicks."""
        action = callback.data
        
        if action == "cmd_start":
            text = handle_start("/start")
            keyboard = get_start_keyboard()
            await callback.message.edit_text(text, reply_markup=keyboard)
        elif action == "cmd_help":
            text = handle_help("/help")
            keyboard = get_help_keyboard()
            await callback.message.edit_text(text, reply_markup=keyboard)
        elif action == "cmd_health":
            text = handle_health("/health")
            await callback.message.answer(text)
        elif action == "cmd_labs":
            text = handle_labs("/labs")
            await callback.message.answer(text)
        elif action == "cmd_scores_lab_04":
            text = handle_scores("/scores lab-04")
            await callback.message.answer(text)
        elif action == "cmd_top_learners":
            text = route_intent("who are the top 5 students in lab 04")
            await callback.message.answer(text)
        elif action == "cmd_sync":
            text = route_intent("sync the data")
            await callback.message.answer(text)
        elif action.startswith("lab_"):
            # Handle lab-specific actions
            parts = action.split("_")
            if len(parts) >= 4:
                lab_id = f"{parts[1]}_{parts[2]}"  # e.g., "lab-04"
                action_type = parts[3]  # e.g., "pass_rates", "timeline"
                
                if action_type == "pass_rates":
                    text = handle_scores(f"/scores {lab_id}")
                elif action_type == "timeline":
                    text = route_intent(f"show timeline for {lab_id}")
                elif action_type == "groups":
                    text = route_intent(f"show groups for {lab_id}")
                elif action_type == "top":
                    text = route_intent(f"top 5 learners in {lab_id}")
                elif action_type == "completion":
                    text = route_intent(f"completion rate for {lab_id}")
                else:
                    text = f"Unknown action: {action_type}"
                
                await callback.message.answer(text)
        
        await callback.answer()

    # Run the bot
    print("Starting Telegram bot...")
    dp.run_polling(bot)


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

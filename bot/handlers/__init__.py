"""Command handlers for the Telegram bot.

Handlers are pure functions that take input and return text.
They don't know about Telegram - same function works from
--test mode, unit tests, or the live bot.
"""

from .commands import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from .intent import route_intent

__all__ = [
    "handle_start",
    "handle_help",
    "handle_health",
    "handle_labs",
    "handle_scores",
    "route_intent",
]

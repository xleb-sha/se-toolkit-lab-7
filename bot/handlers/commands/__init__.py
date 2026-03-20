"""Command handlers implementation.

Each handler is a pure function: takes input, returns text.
No Telegram dependencies - testable in isolation.
"""


def handle_start(text: str) -> str:
    """Handle /start command.

    Args:
        text: The command text (e.g., "/start").

    Returns:
        Welcome message.
    """
    return "Welcome to the LMS Bot! I can help you check system health, browse labs, and view scores. Use /help to see all available commands."


def handle_help(text: str) -> str:
    """Handle /help command.

    Args:
        text: The command text (e.g., "/help").

    Returns:
        List of available commands.
    """
    return """Available commands:
/start - Welcome message
/help - Show this help message
/health - Check backend system status
/labs - List available labs
/scores <lab> - Show pass rates for a specific lab (e.g., /scores lab-04)"""


def handle_health(text: str) -> str:
    """Handle /health command.

    Args:
        text: The command text (e.g., "/health").

    Returns:
        Backend health status.
    """
    # Task 2: Will call LMS API to check backend status
    # For now, return placeholder
    return "Backend status: Not implemented yet. Will check LMS API in Task 2."


def handle_labs(text: str) -> str:
    """Handle /labs command.

    Args:
        text: The command text (e.g., "/labs").

    Returns:
        List of available labs.
    """
    # Task 2: Will fetch from LMS API
    # For now, return placeholder
    return "Available labs: Not implemented yet. Will fetch from LMS API in Task 2."


def handle_scores(text: str) -> str:
    """Handle /scores command.

    Args:
        text: The command text (e.g., "/scores lab-04").

    Returns:
        Pass rates for the specified lab.
    """
    # Task 2: Will fetch from LMS API
    # For now, return placeholder
    return f"Scores for '{text}': Not implemented yet. Will fetch from LMS API in Task 2."

"""Command handlers implementation.

Each handler is a pure function: takes input, returns text.
No Telegram dependencies - testable in isolation.
"""

import httpx
from config import load_config
from services import create_lms_client


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
    try:
        config = load_config()
        client = create_lms_client(config["LMS_API_URL"], config["LMS_API_KEY"])
        items = client.get_items()
        client.close()
        return f"Backend is healthy. {len(items)} items available."
    except httpx.ConnectError as e:
        return f"Backend error: connection refused ({config['LMS_API_URL']}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except httpx.RequestError as e:
        return f"Backend error: {str(e)}. Check your network configuration."
    except Exception as e:
        return f"Backend error: {str(e)}"


def handle_labs(text: str) -> str:
    """Handle /labs command.

    Args:
        text: The command text (e.g., "/labs").

    Returns:
        List of available labs.
    """
    try:
        config = load_config()
        client = create_lms_client(config["LMS_API_URL"], config["LMS_API_KEY"])
        items = client.get_items()
        client.close()

        # Filter for lab-type items (those with type "lab")
        labs = [item for item in items if item.get("type") == "lab"]

        if not labs:
            return "No labs available."

        result = ["Available labs:"]
        for lab in labs:
            # API returns 'title' field, not 'name'
            lab_name = lab.get("title", "Unknown")
            result.append(f"- {lab_name}")

        return "\n".join(result)

    except httpx.ConnectError as e:
        return f"Backend error: connection refused ({config['LMS_API_URL']}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except httpx.RequestError as e:
        return f"Backend error: {str(e)}. Check your network configuration."
    except Exception as e:
        return f"Backend error: {str(e)}"


def handle_scores(text: str) -> str:
    """Handle /scores command.

    Args:
        text: The command text (e.g., "/scores lab-04").

    Returns:
        Pass rates for the specified lab.
    """
    # Parse lab argument
    parts = text.strip().split(maxsplit=1)
    if len(parts) < 2:
        return "Usage: /scores <lab> (e.g., /scores lab-04)"

    lab = parts[1].lower()

    try:
        config = load_config()
        client = create_lms_client(config["LMS_API_URL"], config["LMS_API_KEY"])
        pass_rates = client.get_pass_rates(lab)
        client.close()

        if not pass_rates:
            return f"No pass rate data found for '{lab}'. The lab may not exist yet."

        # Extract lab name from first record if available
        # API returns 'task' and 'avg_score' fields
        lab_name = pass_rates[0].get("lab_name", lab) if pass_rates else lab

        result = [f"Pass rates for {lab_name}:"]
        for record in pass_rates:
            # API returns 'task' not 'task_name', and 'avg_score' not 'pass_rate'
            task_name = record.get("task", "Unknown")
            pass_rate = record.get("avg_score", 0)
            attempts = record.get("attempts", 0)
            result.append(f"- {task_name}: {pass_rate:.1f}% ({attempts} attempts)")

        return "\n".join(result)

    except httpx.ConnectError as e:
        return f"Backend error: connection refused ({config['LMS_API_URL']}). Check that the services are running."
    except httpx.HTTPStatusError as e:
        if e.response.status_code == 404:
            return f"Lab '{lab}' not found. Check the lab identifier."
        return f"Backend error: HTTP {e.response.status_code} {e.response.reason_phrase}. The backend service may be down."
    except httpx.RequestError as e:
        return f"Backend error: {str(e)}. Check your network configuration."
    except Exception as e:
        return f"Backend error: {str(e)}"

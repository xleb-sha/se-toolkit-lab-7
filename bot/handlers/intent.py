"""Intent router for natural language processing.

Routes user messages to LLM for tool-based intent resolution.
Includes fallback handling for greetings and gibberish.
"""

import re
import sys
from config import load_config
from services import create_llm_client


# Patterns for fallback handling
GREETING_PATTERNS = [
    r"\b(hi|hello|hey|greetings|good\s*(morning|afternoon|evening))\b",
    r"\bпривет|здравствуйте|добрый\s*(день|утро|вечер)\b",
]

CAPABILITIES_HINT = """I can help you with:
- "what labs are available?" — List all labs
- "show me scores for lab 4" — Get pass rates for a specific lab
- "who are the top 5 students?" — Get top learners
- "which lab has the lowest pass rate?" — Compare labs
- "how many students are enrolled?" — Get learner count

Or use slash commands: /start, /help, /health, /labs, /scores <lab>"""


def is_greeting(text: str) -> bool:
    """Check if the message is a greeting.

    Args:
        text: User message text.

    Returns:
        True if the message is a greeting.
    """
    text_lower = text.lower()
    for pattern in GREETING_PATTERNS:
        if re.search(pattern, text_lower):
            return True
    return False


def is_gibberish(text: str) -> bool:
    """Check if the message appears to be gibberish.

    Args:
        text: User message text.

    Returns:
        True if the message appears to be gibberish.
    """
    # Very short messages (1-2 chars) are likely gibberish
    if len(text.strip()) <= 2:
        return True
    
    # Check if message has any meaningful words
    # A message with mostly non-alphabetic chars is gibberish
    alpha_chars = sum(1 for c in text if c.isalpha())
    if alpha_chars < len(text.strip()) * 0.3:
        return True
    
    # Check for random keyboard patterns
    gibberish_patterns = [
        r"^(.)\1{4,}$",  # Same char repeated 5+ times (e.g., "aaaaa")
        r"^[asdfghjkl]+$",  # Home row typing
        r"^[qwerty]+$",  # QWERTY row typing
    ]
    text_no_spaces = text.replace(" ", "").lower()
    for pattern in gibberish_patterns:
        if re.match(pattern, text_no_spaces):
            return True
    
    return False


def route_intent(text: str, debug: bool = True) -> str:
    """Route user message through LLM for intent-based processing.

    Args:
        text: User message text.
        debug: If True, print debug info to stderr.

    Returns:
        LLM-generated response or fallback message.
    """
    # Check for greeting
    if is_greeting(text):
        return f"Hello! 👋 {CAPABILITIES_HINT}"
    
    # Check for gibberish
    if is_gibberish(text):
        return f"I didn't understand that. {CAPABILITIES_HINT}"
    
    try:
        config = load_config()
        
        # Check if LLM is configured
        if not config.get("LLM_API_KEY") or not config.get("LLM_API_BASE_URL"):
            return f"LLM is not configured. Please set LLM_API_KEY and LLM_API_BASE_URL in .env.bot.secret.\n\n{CAPABILITIES_HINT}"
        
        llm = create_llm_client(
            api_key=config["LLM_API_KEY"],
            base_url=config["LLM_API_BASE_URL"],
            model=config.get("LLM_API_MODEL", "coder-model"),
        )
        
        try:
            response = llm.chat_with_tools(text, debug=debug)
            return response
        finally:
            llm.close()
            
    except Exception as e:
        # Log full error to stderr for debugging
        print(f"[intent error] {type(e).__name__}: {e}", file=sys.stderr)
        
        # Return user-friendly message with capabilities hint
        error_msg = str(e).lower()
        if "401" in error_msg or "unauthorized" in error_msg:
            return "LLM authentication failed. The API token may have expired. Please restart the LLM proxy.\n\n" + CAPABILITIES_HINT
        elif "connection" in error_msg or "refused" in error_msg:
            return "Cannot connect to LLM service. Please check that the LLM is running.\n\n" + CAPABILITIES_HINT
        elif "timeout" in error_msg:
            return "LLM request timed out. Please try again.\n\n" + CAPABILITIES_HINT
        else:
            return f"LLM error: {e}\n\n" + CAPABILITIES_HINT

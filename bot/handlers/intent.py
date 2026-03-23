"""Intent router for natural language processing.

Routes user messages to LLM for tool-based intent resolution.
Includes fallback handling for greetings and gibberish.
"""

import sys
from config import load_config
from services import create_llm_client


CAPABILITIES_HINT = """I can help you with:
- "what labs are available?" — List all labs
- "show me scores for lab 4" — Get pass rates for a specific lab
- "who are the top 5 students?" — Get top learners
- "which lab has the lowest pass rate?" — Compare labs
- "how many students are enrolled?" — Get learner count

Or use slash commands: /start, /help, /health, /labs, /scores <lab>"""


def is_greeting(text: str) -> bool:
    """Check if the message is a greeting using simple string matching.

    Args:
        text: User message text.

    Returns:
        True if the message is a greeting.
    """
    text_lower = text.lower().strip()
    
    # List of common greetings
    greetings = [
        "hi", "hello", "hey", "greetings", "good morning", "good afternoon", 
        "good evening", "привет", "здравствуйте", "добрый день", "добрый вечер",
    ]
    
    # Check if text starts with or equals any greeting
    for greeting in greetings:
        if text_lower == greeting or text_lower.startswith(greeting + " ") or text_lower.startswith(greeting + "!"):
            return True
    
    return False


def is_gibberish(text: str) -> bool:
    """Check if the message appears to be gibberish using simple heuristics.

    Args:
        text: User message text.

    Returns:
        True if the message appears to be gibberish.
    """
    stripped = text.strip()
    
    # Very short messages (1-2 chars) are likely gibberish
    if len(stripped) <= 2:
        return True
    
    # Check for repeated characters (e.g., "aaaaa", "asdfgh")
    if len(stripped) >= 4:
        # Count unique characters
        unique_chars = len(set(stripped.lower()))
        # If mostly unique chars but all from small keyboard region, likely gibberish
        home_row = set("asdfghjkl")
        qwerty_row = set("qwertyuiop")
        text_chars = set(stripped.lower().replace(" ", ""))
        
        if text_chars and (text_chars <= home_row or text_chars <= qwerty_row):
            return True
    
    # Check for same character repeated many times
    if len(stripped) >= 5:
        first_char = stripped[0].lower()
        if all(c.lower() == first_char for c in stripped if c.isalpha()):
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

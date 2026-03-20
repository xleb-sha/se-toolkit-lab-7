"""Configuration loading from environment variables."""

import os
from pathlib import Path
from dotenv import load_dotenv


def load_config() -> dict[str, str]:
    """Load configuration from .env.bot.secret file.
    
    Returns:
        Dictionary with configuration keys.
    
    Raises:
        ValueError: If required configuration is missing.
    """
    # Determine the path to .env.bot.secret
    bot_dir = Path(__file__).parent
    env_file = bot_dir / ".env.bot.secret"
    
    # Load environment variables from file
    load_dotenv(env_file)
    
    # Collect configuration
    config = {
        "BOT_TOKEN": os.getenv("BOT_TOKEN", ""),
        "LMS_API_URL": os.getenv("LMS_API_URL", ""),
        "LMS_API_KEY": os.getenv("LMS_API_KEY", ""),
        "LLM_API_KEY": os.getenv("LLM_API_KEY", ""),
        "LLM_API_BASE_URL": os.getenv("LLM_API_BASE_URL", ""),
        "LLM_API_MODEL": os.getenv("LLM_API_MODEL", ""),
    }
    
    # Validate required configuration for test mode
    # BOT_TOKEN is only required for actual Telegram bot, not for --test mode
    if not config["LMS_API_URL"]:
        raise ValueError("LMS_API_URL is required")
    if not config["LMS_API_KEY"]:
        raise ValueError("LMS_API_KEY is required")
    
    return config

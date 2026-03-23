"""Inline keyboard definitions for the Telegram bot.

Uses aiogram's InlineKeyboardMarkup for interactive buttons.
"""

from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_start_keyboard() -> InlineKeyboardMarkup:
    """Get inline keyboard for /start command.

    Returns:
        InlineKeyboardMarkup with quick action buttons.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏥 Health Check", callback_data="cmd_health"),
                InlineKeyboardButton(text="📚 Labs", callback_data="cmd_labs"),
            ],
            [
                InlineKeyboardButton(text="📊 Scores Lab 04", callback_data="cmd_scores_lab_04"),
                InlineKeyboardButton(text="🏆 Top Learners", callback_data="cmd_top_learners"),
            ],
            [
                InlineKeyboardButton(text="❓ Help", callback_data="cmd_help"),
            ],
        ],
        resize_keyboard=True,
    )
    return keyboard


def get_help_keyboard() -> InlineKeyboardMarkup:
    """Get inline keyboard for /help command.

    Returns:
        InlineKeyboardMarkup with help buttons.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="🏥 /health", callback_data="cmd_health"),
                InlineKeyboardButton(text="📚 /labs", callback_data="cmd_labs"),
            ],
            [
                InlineKeyboardButton(text="📊 /scores", callback_data="cmd_scores"),
                InlineKeyboardButton(text="👥 /learners", callback_data="cmd_learners"),
            ],
            [
                InlineKeyboardButton(text="🔁 Sync Data", callback_data="cmd_sync"),
            ],
        ],
        resize_keyboard=True,
    )
    return keyboard


def get_lab_actions_keyboard(lab_id: str) -> InlineKeyboardMarkup:
    """Get inline keyboard for lab-specific actions.

    Args:
        lab_id: Lab identifier (e.g., "lab-04").

    Returns:
        InlineKeyboardMarkup with lab action buttons.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="📊 Pass Rates", callback_data=f"lab_{lab_id}_pass_rates"),
                InlineKeyboardButton(text="📈 Timeline", callback_data=f"lab_{lab_id}_timeline"),
            ],
            [
                InlineKeyboardButton(text="👥 Groups", callback_data=f"lab_{lab_id}_groups"),
                InlineKeyboardButton(text="🏆 Top Learners", callback_data=f"lab_{lab_id}_top"),
            ],
            [
                InlineKeyboardButton(text="✅ Completion Rate", callback_data=f"lab_{lab_id}_completion"),
            ],
        ],
        resize_keyboard=True,
    )
    return keyboard


def get_back_keyboard() -> InlineKeyboardMarkup:
    """Get inline keyboard with back button.

    Returns:
        InlineKeyboardMarkup with back button.
    """
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="← Back to Menu", callback_data="cmd_start"),
            ],
        ],
        resize_keyboard=True,
    )
    return keyboard

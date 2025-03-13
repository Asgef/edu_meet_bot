from aiogram.types import InlineKeyboardMarkup
from typing import Dict, List, Callable  # noqa
from datetime import date
from edu_meet_bot.general_menu.models import Order


def select_session(
    sessions: Dict[date, List[Order]],
):
    keyboard = InlineKeyboardMarkup(inline_keyboard=[]) # noqa
    pass

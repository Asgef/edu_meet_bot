from datetime import datetime, timedelta
from edu_meet_bot.session.models import Slot, SlotStatus
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta
from sqlalchemy import select
from typing import Dict, List


async def get_available_slots(db_session: AsyncSession, start_date: date, end_date: date) -> List[Slot]:
    """Get available slots for a specified period."""
    query = select(Slot).where(
        Slot.date >= start_date,
        Slot.date <= end_date,
        Slot.status == SlotStatus.AVAILABLE.value
    )
    result = await db_session.execute(query)
    return result.scalars().all()


def group_slots_by_weeks(slots: List[Slot]) -> Dict[date, List[Slot]]:
    """Group slots by week start date."""
    weeks = {}
    for slot in slots:
        week_start = slot.date.date() - timedelta(days=slot.date.weekday())
        weeks.setdefault(week_start, []).append(slot)
    return weeks


def create_week_selection_keyboard(weeks: Dict[date, List[Slot]]) -> InlineKeyboardMarkup:
    """Create a keyboard to select weeks."""
    keyboard = InlineKeyboardMarkup(inline_keyboard=[])
    for week_start in sorted(weeks.keys()):
        week_label = f"{week_start.strftime('%d.%m.%Y')} - {(week_start + timedelta(days=6)).strftime('%d.%m.%Y')}"
        keyboard.inline_keyboard.append([
            InlineKeyboardButton(
                text=week_label,
                callback_data=f"select_week|{week_start.isoformat()}"
            )
        ])
    return keyboard

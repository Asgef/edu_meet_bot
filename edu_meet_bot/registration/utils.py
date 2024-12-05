from collections import defaultdict
from edu_meet_bot.session.models import Slot, SlotStatus, AcademicSubject, User
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta, time, datetime
from sqlalchemy import select
from typing import Dict, List, Callable, Optional
from functools import wraps
import traceback
import logging


async def get_available_slots(
        db_session: AsyncSession,
        start_date: date,
        end_date: date = None,
        current_time: Optional[time] = None
) -> List[Slot]:
    if end_date is None:
        end_date = start_date + timedelta(days=365)

    # Если current_time не передан, устанавливаем его на полночь
    if current_time is None:
        current_time = time(0, 0)

    query = select(Slot).where(
        # Слоты на будущие дни
        (Slot.date > start_date) |
        # Слоты на сегодня, но позже текущего времени
        ((Slot.date == start_date) & (Slot.time_start > current_time)),
        Slot.date <= end_date,  # Ограничение по конечной дате
        Slot.status == SlotStatus.AVAILABLE.value
    )
    result = await db_session.execute(query)
    return result.scalars().all()


async def get_daily_slots(
        db_session: AsyncSession,
        day: date,
        current_time: Optional[time] = None
) -> List[Slot]:
    if current_time is None:
        current_time = time(0, 0)

    if day == datetime.now().date():
        # Текущий день: учитывать время
        condition = (Slot.time_start > current_time)
    else:
        # Другие дни: брать всё
        condition = True

    query = select(Slot).where(
        Slot.date == day,
        condition,
        Slot.status == SlotStatus.AVAILABLE.value
    )
    result = await db_session.execute(query)
    return result.scalars().all()


async def get_academic_subjects(
        db_session: AsyncSession
) -> List[AcademicSubject]:

    query = select(AcademicSubject)
    result = await db_session.execute(query)
    return result.scalars().all()


async def get_usr_id(db_session: AsyncSession, tg_id: int) -> int:
    query = select(User.id).where(User.tg_id == tg_id)
    result = await db_session.execute(query)
    return result.scalar()


def group_slots_by_time_period(
        slots: List[Slot], period: str, today: date = None
) -> Dict[date, List[Slot]]:
    """Grouping slots by specified period (day, week)."""

    if period == "day":
        key_func: Callable[[Slot], date] = lambda slot: slot.date

    elif period == "week":
        def key_func(slot: Slot) -> date:
            # Начало недели с учетом ограничения на today
            period_start = slot.date - timedelta(
                days=slot.date.weekday()
            )
            return max(period_start, today)

    else:
        raise ValueError(
            f"Unsupported period: {period}. Use 'day' or 'week'."
        )

    grouped_slots = defaultdict(list)
    for slot in slots:
        period_start = key_func(slot)
        grouped_slots[period_start].append(slot)

    return dict(grouped_slots)


async def handle_no_slots(message, period_desc: str):
    await message.answer(f"Нет доступных слотов на выбранный {period_desc}.")


def handle_exceptions(func):
    """Декоратор для обработки исключений."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Ошибка: {e}")
            logging.error(traceback.format_exc())
            if "callback" in kwargs:
                await kwargs["callback"].message.answer(
                    "Произошла ошибка при обработке вашего запроса."
                    "Пожалуйста, попробуйте позже."
                )
            elif args:
                await args[0].message.answer(
                    "Произошла ошибка при обработке вашего запроса."
                    "Пожалуйста, попробуйте позже."
                )
            return None
    return wrapper

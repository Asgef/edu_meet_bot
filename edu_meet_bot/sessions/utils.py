from collections import defaultdict
from edu_meet_bot.general_menu.models import Order, SlotStatus, AcademicSubject, User
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import date, timedelta, time, datetime
from sqlalchemy import select
from typing import Dict, List, Callable, Optional
from sqlalchemy.sql.operators import op
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select
from functools import wraps
import traceback
import logging


async def get_student_orders(
        db_session: AsyncSession, student_id: int, past=False
):
    now = datetime.now()
    query = (select(Order)
    .options(selectinload(Order.slot))
    .where(
        Order.student_id == student_id,
        Order.date > now if not past else Order.date <= now
    ))
    result = await db_session.execute(query)
    return result.scalars().all()




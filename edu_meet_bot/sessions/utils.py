from edu_meet_bot.general_menu.models import Order
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
from sqlalchemy.orm import selectinload
from sqlalchemy.future import select


async def get_student_orders(
        db_session: AsyncSession, student_id: int, past=False
):
    now = datetime.now()
    query = (
        select(Order)
        .options(selectinload(Order.slot))
        .where(
            Order.student_id == student_id,
            Order.date > now if not past else Order.date <= now
        )
    )
    result = await db_session.execute(query)
    return result.scalars().all()

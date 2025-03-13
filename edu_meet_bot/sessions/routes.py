from aiogram import Router, F
from edu_meet_bot.db import async_session
from edu_meet_bot.registration.utils import get_usr_id
from aiogram.types import Message
from edu_meet_bot.sessions.utils import get_student_orders


router = Router(name="edu_meet_bot/registration")


@router.message(F.text == "Мои занятия")
async def get_my_sessions(message: Message):
    user = message.from_user
    student_tg_id = user.id
    async with async_session() as db_session:
        student_id = await get_usr_id(db_session, student_tg_id)
        orders = await get_student_orders(db_session, student_id)

        if not orders:
            await message.answer("❌ У вас пока нет предстоящих занятий.")
            return

    # Формируем список занятий
    sessions_info = "\n\n".join(
        [
            f"📅 Дата: {order.slot.date.strftime('%d.%m.%Y')}\n"
            f"⏰ Время: {order.slot.time_start.strftime('%H:%M')} - "
            f"{order.slot.time_end.strftime('%H:%M')}\n"
            f"📘 Статус: {order.status.value}"
            for order in orders
        ]
    )

    await message.answer(
        f"📚 <b>Ваши предстоящие занятия:</b>\n\n{sessions_info}",
        parse_mode="HTML"
    )

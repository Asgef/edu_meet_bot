from aiogram import Router, F
from datetime import datetime
from edu_meet_bot.db import async_session
from aiogram.fsm.context import FSMContext
from edu_meet_bot.general_menu.enum_fields import OrderStatus, SlotStatus
from edu_meet_bot.settings import TUTOR_TG_ID, PRICE, SUPPORT_CHAT_ID
from edu_meet_bot.general_menu.models import Order, Slot
from aiogram.filters.state import StateFilter
from aiogram.exceptions import TelegramBadRequest
from edu_meet_bot.registration.utils import (
    get_available_slots, group_slots_by_time_period, handle_no_slots,
    handle_exceptions, get_academic_subjects, get_usr_id, get_daily_slots
)
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)

from edu_meet_bot.sessions.utils import get_student_orders
import logging


logger = logging.getLogger(__name__)

router = Router(name="edu_meet_bot/registration")


@router.message(F.text == "Мои занятия")
async def get_my_sessions(message: Message):
    user = message.from_user
    student_tg_id = user.id
    async with async_session() as db_session:
        student_id = await get_usr_id(db_session, student_tg_id)
        orders = await get_student_orders(db_session, student_id)
        logging.info(f"Orders >>>>>>>>>>>>>>>>>>>>: {orders}")

        if not orders:
            await message.answer("❌ У вас пока нет предстоящих занятий.")
            return

    # Формируем список занятий
    sessions_info = "\n\n".join(
        [
            f"📅 Дата: {order.slot.date.strftime('%d.%m.%Y')}\n"
            f"⏰ Время: {order.slot.time_start.strftime('%H:%M')} - {order.slot.time_end.strftime('%H:%M')}\n"
            f"📘 Статус: {order.status.value}"
            for order in orders
        ]
    )

    await message.answer(
        f"📚 <b>Ваши предстоящие занятия:</b>\n\n{sessions_info}",
        parse_mode="HTML"
    )
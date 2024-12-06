from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from edu_meet_bot.registration.views import select_date
from datetime import datetime
from edu_meet_bot.db import async_session
import logging
from edu_meet_bot.registration.utils import (
    get_available_slots, group_slots_by_time_period, handle_no_slots,
    handle_exceptions, get_academic_subjects, get_usr_id, get_daily_slots
)
from edu_meet_bot.registration.views import (
    select_week, select_slot, select_day, register_button,
    register_button_academic_subject
)
from aiogram.fsm.context import FSMContext
from edu_meet_bot.session.enum_fields import OrderStatus, SlotStatus
from edu_meet_bot.settings import TUTOR_TG_ID, PRICE, SUPPORT_CHAT_ID
from edu_meet_bot.session.models import Order, Slot
from aiogram.filters.state import StateFilter
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


logger = logging.getLogger(__name__)

router = Router(name="edu_meet_bot/registration")


@router.message(F.text == "Записаться на занятие")
async def receive_registration_request(message: Message) -> None:
    await message.answer(
        "🎓 <b>Запись на занятие</b>\n\n"
        f"💵 <b>Цена:</b> {PRICE} ₽ / час\n"
        "📅 <i>Выберите удобный день и время для занятия.</i>\n\n"
        "⚠️ После предоплаты 50% ваш заказ будет подтверждён.\n\n"
        "➡️ <b>Начнём?</b>",
        reply_markup=select_date(
            user_id=message.from_user.id, user_name=message.from_user.username
        ),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith('select_date|'))
@handle_exceptions
async def on_select_date_click(callback: CallbackQuery) -> None:
    today = datetime.now().date()  # Текущая дата
    now_time = datetime.now().time()  # Текущее время
    logging.info(f'Сегодня >>>>>>>>>>>>>: {today}, Текущее время: {now_time}')

    async with async_session() as db_session:
        # Получаем доступные слоты
        slots = await get_available_slots(
            db_session, start_date=today, current_time=now_time
        )

    if not slots:
        await handle_no_slots(callback.message, "месяц")
        return

    logging.info(f'Слоты >>>>>>>>>>>>>>>>>: {slots}')

    # Группируем слоты по неделям
    weeks = group_slots_by_time_period(slots, period='week', today=today)

    # Создаем клавиатуру для выбора недели
    keyboard = select_week(
        weeks,
        label_func = lambda start, end: f"📅 {start.strftime('%d.%m')} - "
                                        f"{end.strftime('%d.%m.%Y')}",
        callback_prefix="select_week"
    )

    # Отправляем сообщение с выбором недели
    await callback.message.edit_text(
        "📅 <b>Выберите неделю для записи:</b>\n\n"
        "Нажмите на одну из кнопок ниже, чтобы выбрать диапазон дат.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith('select_week|'))
@handle_exceptions
async def on_select_week_click(callback: CallbackQuery) -> None:
    _, week_start_str, week_end_str = callback.data.split('|')
    week_start = datetime.fromisoformat(week_start_str).date()
    week_end = datetime.fromisoformat(week_end_str).date()

    async with async_session() as db_session:
        # Получаем слоты в пределах выбранной недели
        slots = await get_available_slots(db_session, week_start, week_end)

    logging.info(f'Недельные слоты >>>>>>>>>>>>>>>>>: {slots}')

    if not slots:
        await handle_no_slots(
            callback.message,
            f"неделю с {week_start.strftime('%d.%m.%Y')} по "
            f"{week_end.strftime('%d.%m.%Y')}"
        )
        return

    # Группируем слоты по дням
    days = group_slots_by_time_period(slots, period='day')

    # Создаем клавиатуру для выбора дня
    keyboard = select_day(
        period=days,
        label_func=lambda day: f"📅 {day.strftime('%A, %d.%m.%Y')}",
        callback_prefix="select_day"
    )

    # Отправляем сообщение с выбором дня
    await callback.message.edit_text(
        f"📅 <b>Выберите день недели:</b>\n\n"
        f"📆 <i>Диапазон:</i> {week_start.strftime('%d.%m.%Y')} - "
        f"{week_end.strftime('%d.%m.%Y')}\n\n"
        f"⬇️ Нажмите на один из дней ниже, чтобы выбрать удобное время.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    logging.info("Сообщение с выбором дня отправлено.")


@router.callback_query(F.data.startswith('select_day|'))
@handle_exceptions
async def on_select_day_click(callback: CallbackQuery) -> None:
    # Извлекаем дату дня из callback_data
    _, day_str = callback.data.split('|')
    selected_day = datetime.fromisoformat(day_str).date()

    async with async_session() as db_session:
        # Получаем доступные слоты для выбранного дня
        slots = await get_daily_slots(
            db_session, selected_day, datetime.now().time()
        )
    slots.sort(key=lambda slot: slot.time_start)
    logging.info(f'Слоты для дня >>>>>>>>>>>>>> {selected_day}: {slots}')

    # Проверяем, есть ли доступные слоты
    if not slots:
        return await handle_no_slots(callback.message, period_desc="день")

    # Создаем клавиатуру для выбора времени
    keyboard = select_slot(
        slots,
        label_func=lambda
        slot: f"🕒 {slot.time_start.strftime('%H:%M')} - "
              f"{slot.time_end.strftime('%H:%M')}",
        callback_prefix="select_slot"
    )

    # Отправляем сообщение с выбором времени
    await callback.message.edit_text(
        f"🕒 <b>Выберите удобное время:</b>\n\n"
        f"📅 <i>Дата:</i> {selected_day.strftime('%A, %d.%m.%Y')}\n\n"
        f"⬇️ Нажмите на одно из доступных временных окон ниже.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    logging.info("Сообщение с выбором времени отправлено.")


@router.callback_query(F.data.startswith('select_slot|'))
@handle_exceptions
async def on_select_slot_click(callback: CallbackQuery) -> None:
    # Извлекаем данные из callback_data
    _, slot_id, slot_time, slot_date = callback.data.split('|')
    slot_id = int(slot_id)

    # Отправляем сообщение с информацией о выбранном слоте
    await callback.message.edit_text(
        f"🎓 <b>Регистрация на занятие!</b>\n\n"
        f"📅 <b>Дата:</b> {slot_date}\n"
        f"⏰ <b>Время:</b> {slot_time}\n\n"
        f"📘 <i>Выберите учебный предмет на следующем шаге.</i>",
        reply_markup=register_button(slot_id),
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith('register_academic_subject|'))
@handle_exceptions
async def on_register_subject_click(
        callback: CallbackQuery, state: FSMContext
) -> None:
    # Извлекаем slot_id из callback_data
    _, slot_id = callback.data.split('|')
    slot_id = int(slot_id)

    # Сохраняем slot_id в FSM
    await state.update_data(slot_id=slot_id)

    # Получаем список предметов
    async with async_session() as db_session:
        subjects = await get_academic_subjects(db_session)

    # Создаем клавиатуру для выбора предмета
    keyboard = register_button_academic_subject(subjects)

    # Отправляем сообщение пользователю
    await callback.message.edit_text(
        "📘 <b>Выберите учебный предмет:</b>\n\n"
        "⬇️ Нажмите на один из вариантов ниже.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )


@router.callback_query(F.data.startswith('select_subject|'))
@handle_exceptions
async def on_subject_selected(
        callback: CallbackQuery, state: FSMContext
) -> None:
    # Извлекаем subject_id из callback_data
    _, subject_id, subject_name = callback.data.split('|')
    subject_id = int(subject_id)

    # Сохраняем subject_id в FSM
    await state.update_data(subject_id=subject_id, subject_name=subject_name)

    # Создаём клавиатуру с кнопкой "Пропустить"
    keyboard = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Пропустить", callback_data="skip_comment"
                )
            ]
        ]
    )

    # Сообщение пользователю о вводе комментария
    sent_message = await callback.message.edit_text(
        "✍️ <b>Напишите комментарий:</b>\n\n"
        "Это может быть:\n"
        "— Ваше имя\n"
        "— Вопросы или пожелания\n\n"
        "💡 Если комментарий не нужен, нажмите 'Пропустить'.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )

    # Сохраняем ID сообщения с кнопкой "Пропустить"
    await state.update_data(skip_message_id=sent_message.message_id)
    # Устанавливаем состояние ожидания комментария
    await state.set_state("waiting_for_comment")


@router.callback_query(F.data == "skip_comment")
@handle_exceptions
async def on_skip_comment(callback: CallbackQuery, state: FSMContext) -> None:
    # Подтверждаем обработку callback-запроса
    await callback.answer()

    # Извлекаем данные из FSM
    data = await state.get_data()
    slot_id = data["slot_id"]
    subject_id = data["subject_id"]
    subject_name = data["subject_name"]

    logging.info(f"Callback user id >>>>>: {callback.from_user.id}")

    # Завершаем регистрацию с пустым комментарием
    await finish_registration(
        state=state,
        message_object=callback.message,
        slot_id=slot_id,
        subject_id=subject_id,
        subject_name=subject_name,
        user_id=callback.from_user.id,
        comment=""
    )

    # Убираем клавиатуру после завершения
    await callback.message.edit_reply_markup(reply_markup=None)


@router.message(StateFilter("waiting_for_comment"))
@handle_exceptions
async def on_comment_entered(message: Message, state: FSMContext) -> None:
    # Получаем введённый комментарий
    comment = message.text

    # Извлекаем данные из FSM
    data = await state.get_data()
    slot_id = data["slot_id"]
    subject_id = data["subject_id"]
    subject_name = data["subject_name"]

    # Удаляем предыдущее сообщение с "Пропустить", если оно существует
    skip_message_id = data.get("skip_message_id")
    if skip_message_id:
        try:
            await message.bot.delete_message(chat_id=message.chat.id,
                                             message_id=skip_message_id)
        except Exception as e:
            logging.error(f"Не удалось удалить сообщение: {e}")

    # Завершаем регистрацию с введённым комментарием
    await finish_registration(
        state=state,
        message_object=message,
        slot_id=slot_id,
        subject_id=subject_id,
        user_id=message.from_user.id,
        subject_name=subject_name,
        comment=comment
    )


async def finish_registration(
        state: FSMContext,
        message_object: Message | CallbackQuery,
        slot_id: int,
        subject_id: int,
        subject_name: str,
        user_id: int,
        comment: str,
) -> None:
    async with async_session() as db_session:
        # Получаем student_id по user_id
        student_id = await get_usr_id(db_session, user_id)
        logging.info(
            f"Resolved student_id: {student_id} for user_id: {user_id}"
        )

        if not student_id:
            await message_object.answer(
                "❌ Ошибка: не удалось найти пользователя в базе данных."
            )
            await state.clear()
            return

        tutor_id = await get_usr_id(db_session, TUTOR_TG_ID)
        slot = await db_session.get(Slot, slot_id)

        # Проверяем статус слота
        if slot.status != SlotStatus.AVAILABLE:
            await message_object.answer(
                "❌ Слот уже занят. Пожалуйста, выберите другой."
            )
            await state.clear()
            return

        # Обновляем статус слота
        slot.status = SlotStatus.PENDING
        slot.student_id = student_id

        # Создаём заказ
        order = Order(
            student_id=student_id,
            tutor_id=tutor_id,
            slot_id=slot_id,
            subject_id=subject_id,
            status=OrderStatus.PENDING,
            comment=comment,
            date=slot.date,
        )
        db_session.add(order)
        await db_session.commit()

    # Отправляем сообщение пользователю
    formatted_date = slot.date.strftime("%d.%m.%Y")
    registration_message = (
        f"✅ <b>Вы успешно зарегистрировались на занятие!</b>\n\n"
        f"📅 <b>Дата:</b> {formatted_date} {slot.time_start.strftime('%H:%M')}-"
        f"{slot.time_end.strftime('%H:%M')}\n"
        f"📘 <b>Предмет:</b> {subject_name}\n"
        f"💬 <b>Комментарий:</b> {'Не указан' if not comment else comment}"
    )

    # Получаем имя пользователя (универсально для Message и CallbackQuery)
    user = message_object.from_user
    username = user.username
    user_first_name = user.first_name
    user_name = username if username else user_first_name

    # Обновляем текст сообщения, если это сообщение бота
    if isinstance(message_object, CallbackQuery):
        await message_object.message.edit_text(
            registration_message, parse_mode="HTML"

        )
        # Получаем бот из CallbackQuery,
        # что бы отправить уведомление в чат поддержки
        bot = message_object.bot
    else:
        # Отправляем новое сообщение, если это пользовательское сообщение
        await message_object.answer(registration_message, parse_mode="HTML")
        bot = message_object.bot  # Получаем бот из Message

    logging.info(
        f"Отправка уведомления в SUPPORT_CHAT_ID: {SUPPORT_CHAT_ID}"
    )
    logging.info("")
    await bot.send_message(
        chat_id=SUPPORT_CHAT_ID,
        text=(
            f"🔥 <b>Новый заказ!</b> 🔥\n\n"
            f"👤 <b>Пользователь:</b> {user_name}\n"
            f"📅 <b>Дата:</b> {formatted_date} "
            f"{slot.time_start.strftime('%H:%M')}-"
            f"{slot.time_end.strftime('%H:%M')}\n"
            f"📘 <b>Предмет:</b> {subject_name}\n"
            f"💬 <b>Комментарий:</b> {'Не указан' if not comment else comment}"
        ),
        parse_mode='HTML'
    )

    # Очистка состояния
    await state.clear()

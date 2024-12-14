from aiogram import Router, F
from datetime import datetime
from edu_meet_bot.db import async_session
from aiogram.fsm.context import FSMContext
from edu_meet_bot.session.enum_fields import OrderStatus, SlotStatus
from edu_meet_bot.settings import TUTOR_TG_ID, PRICE, SUPPORT_CHAT_ID
from edu_meet_bot.session.models import Order, Slot
from aiogram.filters.state import StateFilter
from edu_meet_bot.support.views import answer_button
from aiogram.exceptions import TelegramBadRequest
from edu_meet_bot.registration.utils import (
    get_available_slots, group_slots_by_time_period, handle_no_slots,
    handle_exceptions, get_academic_subjects, get_usr_id, get_daily_slots
)
from edu_meet_bot.registration.views import (
    select_week, select_slot, select_day, academic_subject_button
)
from aiogram.types import (
    Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
)
import logging


logger = logging.getLogger(__name__)

router = Router(name="edu_meet_bot/registration")


@router.message(F.text == "Записаться на занятие")
@handle_exceptions
async def on_register_subject_click(
        message: Message, state: FSMContext
) -> None:
    await state.clear()  # Предварительно очищаем состояние

    # Подготавливаем данные пользователя и сохраняем в состояние
    user = message.from_user
    student_tg_id = user.id
    username = user.username
    user_first_name = user.first_name
    student_name = username if username else user_first_name

    async with async_session() as db_session:
        student_id = await get_usr_id(db_session, student_tg_id)
        tutor_id = await get_usr_id(db_session, TUTOR_TG_ID)

    await state.update_data(
        student_name=student_name, student_id=student_id,
        student_tg_id=student_tg_id, tutor_id=tutor_id
    )

    # Получаем список предметов
    async with async_session() as db_session:
        subjects = await get_academic_subjects(db_session)

    # Создаем клавиатуру для выбора предмета
    keyboard = academic_subject_button(subjects)

    # Отправляем сообщение пользователю
    await message.answer(
        "📘 <b>Выберите учебный предмет:</b>\n\n"
        "⬇️ Нажмите на один из вариантов ниже.",
        reply_markup=keyboard,
        parse_mode="HTML"
    )
    # Ждём нажатия кнопки
    await state.set_state("waiting_for_subject")


@router.callback_query(F.data == "back_to_subjects")
@handle_exceptions
async def back_to_subjects(callback: CallbackQuery, state: FSMContext) -> None:
    # Перенаправляем на хендлер выбора предмета
    await on_register_subject_click(callback.message, state)


@router.callback_query(F.data.startswith('select_date|'))
async def on_subject_selected(
        callback: CallbackQuery, state: FSMContext
) -> None:
    parts = callback.data.split('|')

    if len(parts) == 3:
        # Если данные о предмете пришли
        # Извлекаем информацию о выбранном предмете и запоминаем ее
        _, subject_id_str, subject_name = parts
        subject_id = int(subject_id_str)
        # Сохраняем выбранный предмет в состояние
        await state.update_data(
            subject_id=subject_id, subject_name=subject_name
        )

    # Если произошёл возврат из кнопки "Назад", просто продолжаем
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
        label_func=lambda start, end:
        f"📅 {start.strftime('%d.%m')} - {end.strftime('%d.%m.%Y')}",
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
        callback_prefix="select_day",
        week_start=week_start_str,
        week_end=week_end_str
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
    _, day_str, week_start_str, week_end_str = callback.data.split('|')
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
        callback_prefix="select_slot",
        week_start=week_start_str,
        week_end=week_end_str
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
async def on_slot_selected(
        callback: CallbackQuery, state: FSMContext
) -> None:
    # Извлекаем слот и предмет из callback_data
    _, slot_id, slot_time, slot_date = callback.data.split('|')
    slot_id = int(slot_id)

    # Сохраняем слот в FSM
    await state.update_data(
        slot_id=slot_id, slot_time=slot_time, slot_date=slot_date
    )

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

    comment = ''
    await state.update_data(comment=comment)

    # Подтверждаем регистрацию с пустым комментарием
    await confirm_registration(callback.message, state, is_callback=True)


@router.message(StateFilter("waiting_for_comment"))
@handle_exceptions
async def on_comment_entered(message: Message, state: FSMContext) -> None:
    # Получаем введённый комментарий
    comment = message.text
    await state.update_data(comment=comment)

    # Извлекаем данные из FSM
    data = await state.get_data()

    # Удаляем предыдущее сообщение с "Пропустить", если оно существует
    skip_message_id = data.get("skip_message_id")
    if skip_message_id:
        try:
            await message.bot.delete_message(
                chat_id=message.chat.id, message_id=skip_message_id
            )
        except Exception as e:
            logging.error(f"Не удалось удалить сообщение: {e}")

    # Переходим к подтверждению
    await confirm_registration(message, state, is_callback=False)


async def confirm_registration(
        message: Message, state: FSMContext, is_callback: bool
) -> None:
    data = await state.get_data()

    confirmation_text = (
        f"✅ <b>Проверьте данные:</b>\n\n"
        f"📘 <b>Предмет:</b> {data['subject_name']}\n"
        f"📅 <b>Дата:</b> {data['slot_date']}\n"
        f"⏰ <b>Время:</b> {data['slot_time']}\n"
        f"💬 <b>Комментарий:</b> "
        f"{'Не указан' if not data['comment'] else data['comment']}\n\n"
        f"💵 <b>Цена:</b> {PRICE} ₽ / час\n"
        "⚠️ После предоплаты 50% ваш заказ будет подтверждён.\n\n"
        "💡 Нажмите 'Подтвердить', чтобы завершить регистрацию."
    )

    # Отправляем финальное сообщение
    if is_callback:
        await message.edit_text(
            confirmation_text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="Подтвердить", callback_data="confirm_registration"
                    )]
                ]
            ),
            parse_mode="HTML"
        )
    else:
        await message.answer(
            confirmation_text,
            reply_markup=InlineKeyboardMarkup(
                inline_keyboard=[
                    [InlineKeyboardButton(
                        text="Подтвердить", callback_data="confirm_registration"
                    )]
                ]
            ),
            parse_mode="HTML"
        )

    await state.set_state("registration_confirmed")


@router.callback_query(F.data == "confirm_registration")
@handle_exceptions
async def registration(callback: CallbackQuery, state: FSMContext) -> None:
    data = await state.get_data()

    # Логирование для отладки
    logging.info(f"Registration data >>>>>>>>>>>>>>>>>>>>: {data}")

    # Проверяем статус слота
    async with async_session() as db_session:
        try:
            slot = await db_session.get(Slot, data["slot_id"])
            if slot.status != SlotStatus.AVAILABLE:
                await callback.answer(
                    "❌ Слот уже занят. Пожалуйста, "
                    "повторите регистрацию и выберите другой слот."
                )
                await state.clear()
                return

            # Обновляем статус слота
            slot.status = SlotStatus.PENDING
            slot.student_id = data["student_id"]

            # Создаём заказ
            order = Order(
                student_id=data["student_id"],
                tutor_id=data["tutor_id"],
                slot_id=data["slot_id"],
                subject_id=data["subject_id"],
                status=OrderStatus.PENDING,
                comment=data.get("comment"),
                date=slot.date,
            )
            db_session.add(order)
            await db_session.commit()
        finally:
            await db_session.close()

    registration_message = (
        f"✅ <b>Вы успешно зарегистрировались на занятие!</b>\n\n"
        f"📅 <b>Дата:</b> {data["slot_date"]} "
        f"{slot.time_start.strftime('%H:%M')}-"
        f"{slot.time_end.strftime('%H:%M')}\n"
        f"📘 <b>Предмет:</b> {data['subject_name']}\n"
        f"💬 <b>Комментарий:</b> "
        f"{'Не указан' if not data['comment'] else data['comment']}"
    )

    # отправляем соответствующее сообщение пользователю
    await callback.message.edit_text(registration_message, parse_mode="HTML")

    # Логирование отправки уведомления
    logging.info(
        f"Отправка уведомления в SUPPORT_CHAT_ID >>>>>>> : {SUPPORT_CHAT_ID}"
    )

    # Отправляем уведомление в чат поддержки
    bot = callback.bot
    try:
        await bot.send_message(
            chat_id=SUPPORT_CHAT_ID,
            text=(
                f"🔥 <b>Новый заказ!</b> 🔥\n\n"
                f"👤 <b>Пользователь:</b> {data['student_name']}\n"
                f"📅 <b>Дата:</b> {data["slot_date"]} "
                f"{slot.time_start.strftime('%H:%M')}-"
                f"{slot.time_end.strftime('%H:%M')}\n"
                f"📘 <b>Предмет:</b> {data['subject_name']}\n"
                f"💬 <b>Комментарий:</b> "
                f"{'Не указан' if not data['comment'] else data['comment']}"
            ),
            parse_mode='HTML',
            reply_markup=answer_button(
                data["student_tg_id"], data["student_name"]
            )
        )
        logging.info("Уведомление успешно отправлено в чат поддержки.")
    except TelegramBadRequest as e:
        logging.error(f"Ошибка при отправке уведомления в чат поддержки: {e}")

    # Очистка состояния
    await state.clear()

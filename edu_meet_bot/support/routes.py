from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from edu_meet_bot.support.fsm import StepsQuestionMessage, StepsAnswerMessage
from aiogram.fsm.context import FSMContext
from edu_meet_bot import settings
from edu_meet_bot.support.utils import escape_markdown
from edu_meet_bot.support.views import answer_button
# from edu_meet_bot.debug.utils import log_json_data


router = Router(name="edu_meet_bot/support")


@router.message(Command("getchatid"))
# @log_json_data
async def get_chat_id(message: Message):
    chat_id = message.chat.id
    user_id = message.from_user.id
    await message.answer(
        f"Chat id is: *{chat_id}*\n"
        f"Your id is: *{user_id}*", parse_mode='Markdown'
    )


@router.message(F.text == "Связаться с репетитором")
async def get_client_question(message: Message, state: FSMContext) -> None:
    await message.answer(
        'Задайте ваш вопрос репетитору, он ответит как только освободится:'
    )
    await state.set_state(StepsQuestionMessage.GET_MASSAGE)


@router.callback_query(F.data.startswith('answer|'))
async def on_answer_click(callback: CallbackQuery, state: FSMContext) -> None:
    callback_data = callback.data.split('|')
    user_id, user_name = int(callback_data[1]), callback_data[2]
    await state.update_data(user_id=user_id, user_name=user_name)
    await state.set_state(StepsAnswerMessage.GET_MASSAGE)
    await callback.message.answer(
        f"Введите текст ответа для пользователя {user_name}.",
        parse_mode='Markdown'
    )
    await callback.answer()


@router.message(StepsQuestionMessage.GET_MASSAGE)
async def send_client_question_massage(
        message: Message, state: FSMContext, bot: Bot
) -> None:
    user_name = message.from_user.username or message.from_user.first_name
    question = message.caption\
        if message.content_type == 'photo' else message.text

    # Обработка спецсимволов для Markdown (базового)
    user_name = escape_markdown(user_name)
    question = escape_markdown(question)

    if message.content_type == 'photo' and message.photo:
        photo_id = message.photo[-1].file_id
        await bot.send_photo(
            settings.SUPPORT_CHAT_ID,
            photo=photo_id,
            caption=(
                f"✉ | Новый вопрос\nОт: {user_name}\nВопрос: `{question}`\n\n"
                f"📝 👇"
            ),
            parse_mode='Markdown',
            reply_markup=answer_button(message.from_user.id, user_name)
        )
    else:
        await bot.send_message(
            settings.SUPPORT_CHAT_ID,
            text=(
                f"✉ | Новый вопрос\nОт: {user_name}\nВопрос: `{question}`\n\n"
                f"📝 👇"
            ),
            parse_mode='Markdown',
            reply_markup=answer_button(message.from_user.id, user_name)
        )

    await message.reply(
        'Ваш вопрос был отослан! Ожидайте ответа.',
        parse_mode='Markdown'
    )
    await state.clear()


@router.message(StepsAnswerMessage.GET_MASSAGE)
async def get_admin_answer(
        message: Message, state: FSMContext, bot: Bot
) -> None:
    data = await state.get_data()
    user_id = data.get('user_id')
    user_name = data.get('user_name')
    answer = message.text

    # Отправляем ответ пользователю
    await bot.send_message(

        user_id,
        f"✉ Новое сообщение!\nОтвет от репетитора:\n\n`{answer}`",
        parse_mode='Markdown'
    )

    # Уведомляем администратора об успешной отправке
    await message.answer(
        f"✅ Вы успешно ответили пользователю {user_name}.",
        parse_mode='Markdown'
    )
    await state.clear()  # Очищаем состояние после отправки ответа

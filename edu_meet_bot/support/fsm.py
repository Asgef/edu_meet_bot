from aiogram.fsm.state import State, StatesGroup


class StepsQuestionMessage(StatesGroup):
    GET_MASSAGE = State()


class StepsAnswerMessage(StatesGroup):
    GET_MASSAGE = State()

from edu_meet_bot.errors import TutorBotError


class InvalidUserIdError(TutorBotError):

    def __init__(self) -> None:
        super().__init__("Не корректный ID пользователя или структура ответа")
class TutorBotError(Exception):

    def __init__(self, message: str) -> None:
        self.message = message

    def __repr__(self) -> str:
        return self.message


class InvalidUserError(TutorBotError):

    def __init__(self) -> None:
        super().__init__("Некорректный пользователь")


class UserNotFoundError(TutorBotError):

    def __init__(self) -> None:
        super().__init__("Пользователь не найден")

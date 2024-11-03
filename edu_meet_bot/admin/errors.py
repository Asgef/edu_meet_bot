from edu_meet_bot.errors import TutorBotError


class UserAlreadyAdmin(TutorBotError):

    def __init__(self) -> None:
        super().__init__("Пользователь уже является админом")


class AdminRestrictionError(TutorBotError):

    def __init__(self) -> None:
        super().__init__("Доступно только для администраторов")


class UserAlreadyIsNotAdmin(TutorBotError):

    def __init__(self) -> None:
        super().__init__("Пользователь уже не является администратором")


class UserNeverBeenAdmin(TutorBotError):

    def __init__(self) -> None:
        super().__init__(
            "Данный пользователь никогда и не был администратором")

class NoTextMessageException(Exception):
    pass


class ScoreOutOfRange(Exception):
    pass


class UserNotFound(Exception):
    pass


class PlaceNotFound(Exception):
    pass


class MessageIsTooLarge(Exception):
    def __init__(self, *args, message_size: int, max_size: int):
        super().__init__(*args)
        self.message_size = message_size
        self.max_size = max_size

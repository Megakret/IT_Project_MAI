from aiogram.methods.send_message import SendMessage
from tg_bot.tg_exceptions import MessageIsTooLarge


async def message_sender_wrap(sender: SendMessage):
    await sender


def shorten_message(message: str, max_size: int):
    if len(message) <= max_size:
        return message
    return message[:max_size].strip() + "..."


# will use after merge
def validate_message_size(message: str, max_size: int):
    if len(message) > max_size:
        raise MessageIsTooLarge(message_size=len(message), max_size=max_size)
    return message

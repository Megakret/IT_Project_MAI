from aiogram.methods.send_message import SendMessage
from tg_bot.tg_exceptions import MessageIsTooLarge
from tg_bot.ui_components.RetryPolicyChecker import REQUEST_TAG, RetryPolicyRequest
from aiogram.fsm.context import FSMContext


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


async def drop_request(state: FSMContext):
    data = await state.get_data()
    current_request: RetryPolicyRequest = data.get(REQUEST_TAG, None)
    if current_request is not None:
        await current_request.drop_request()
    await state.update_data(**{REQUEST_TAG: None})
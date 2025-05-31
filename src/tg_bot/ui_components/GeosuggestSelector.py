import asyncio
from aiogram.types import Message, CallbackQuery
from aiogram.methods.send_message import SendMessage
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from api.geosuggest.geosuggest_yandex import GeosuggestResult, GeosuggestYandex
from api.geosuggest.place import Place
from tg_bot.utils_and_validators import message_sender_wrap
from tg_bot.keyboards import suggest_place_kbs
from tg_bot.tg_exceptions import NoTextMessageException


PLACE_KEY = "place"
KEYBOARD_PREFIX = "suggest_place"


class NoPlacesFoundException(Exception):
    pass


class GeosuggestSelector:
    """Class for handling geosuggest menu.\n

    Keyword arguments:\n
    selector_state (State): State in which user selects place.\n
    """

    def __init__(self, selector_state: State):
        self._selector_state = selector_state

    async def show_suggestions(self, message: Message, state: FSMContext):
        """Shows geosuggest menu and changes state. Invoke by yourself.\n

        Keyword arguments:\n
        message (Message): message to which bot answers with the menu.\n
        state (FSMContext): user's fsm\n
        """

        try:
            place_name: str = message.text
            if len(place_name) == 0:
                raise NoTextMessageException()
            responce: GeosuggestResult = await GeosuggestYandex.request(message.text)
            if len(responce.get_places()) == 0:
                raise NoPlacesFoundException()
            senders: list[asyncio.Task] = []
            await message.answer("Какое из следующих мест вы имели в виду?")
            await state.update_data(places=responce)
            for i, place in enumerate(responce.get_messages()):
                message_obj: SendMessage = message.answer(
                    place, reply_markup=suggest_place_kbs[i]
                )
                senders.append(asyncio.create_task(message_sender_wrap(message_obj)))
            await asyncio.wait(senders)
            await state.set_state(self._selector_state)
        except NoTextMessageException:
            await message.answer("Введите название места текстом")
        except NoPlacesFoundException:
            await message.answer(
                "Упс, кажется мы не нашли такого места. Попробуйте ввести его иначе."
            )

    async def selected_place(
        self, callback: CallbackQuery, state: FSMContext
    ):  # only call from Selector's buttons. Adds place to FSMContext
        """Invoke from selector's buttons. Use filter like F.data.contains(KEYBOARD_PREFIX).\n
        Puts chosen place in FSMContext data by tag "place"(or PLACE_KEY).\n

        Keyword arguments:\n
        callback: callback from geosuggest button\n
        state: user's fsm\n
        """

        callback_data: str = callback.data
        place_id = int(callback_data[-1])
        data = await state.get_data()
        responce: GeosuggestResult = data["places"]
        chosen_place: Place = responce[place_id]
        await state.update_data({PLACE_KEY: chosen_place})
        await callback.answer(f"Вы выбрали {chosen_place.get_name()}")

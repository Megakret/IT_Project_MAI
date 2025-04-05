from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.methods.send_message import SendMessage
from aiogram.types import ReplyKeyboardRemove
from aiogram import F
import asyncio
from api.geosuggest.geosuggest import Geosuggest, GeosuggestResult
from api.geosuggest.place import Place
from tg_bot.keyboards import suggest_place_kbs, starter_kb
from tg_bot.aiogram_coros import message_sender_wrap, custom_clear

router = Router()


class ScoreOutOfRange(Exception):
    pass


class NewPlaceFSM(StatesGroup):
    enter_place = State()
    choose_place = State()
    enter_description = State()
    enter_score = State()


@router.message(CommandStart())
async def handle_cmd_start(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Привет. Напиши /add_place, чтобы добавить место для досуга",
        reply_markup=starter_kb,
    )
    await state.clear()


@router.message(Command("add_place"))
async def geosuggest_test(message: Message, state: FSMContext) -> None:
    await custom_clear(state)
    await message.answer(
        "Введите место для досуга: ", reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(NewPlaceFSM.enter_place)


@router.message(NewPlaceFSM.enter_place)
async def check_place(message: Message, state: FSMContext):
    responce: GeosuggestResult = await Geosuggest.request(message.text)
    if len(responce) == 0:
        await message.answer(
            "Упс, кажется мы не нашли такого места. Попробуйте ввести его иначе."
        )
        return None
    senders: list[asyncio.Task] = []
    await message.answer("Какое из следующих мест вы имели в виду?")
    await state.update_data(places=responce, name=message.text)
    for i, place in enumerate(responce.get_messages()):
        message_obj: SendMessage = message.answer(
            place, reply_markup=suggest_place_kbs[i]
        )
        senders.append(asyncio.create_task(message_sender_wrap(message_obj)))
    await asyncio.wait(senders)
    await state.set_state(NewPlaceFSM.choose_place)


@router.callback_query(F.data.contains("suggest_place"), NewPlaceFSM.choose_place)
async def choose_suggested_place(callback: CallbackQuery, state: FSMContext):
    callback_data: str = callback.data
    place_id = int(callback_data[-1])
    data = await state.get_data()
    responce: GeosuggestResult = data["places"]
    chosen_place: Place = responce[place_id]
    await state.update_data(place=chosen_place)
    await callback.answer(f"Вы выбрали {chosen_place.get_name()}")
    await callback.message.answer("Введите свое описание места")
    await state.set_state(NewPlaceFSM.enter_description)


@router.message(NewPlaceFSM.enter_description)
async def enter_description(message: Message, state: FSMContext):
    description: str = message.text
    await state.update_data(description=description)
    await message.answer("Дайте оценку месту от 1 до 10")
    await state.set_state(NewPlaceFSM.enter_score)


async def answer_form_result(message: Message, state: FSMContext):
    data = await state.get_data()
    place: Place = data["place"]
    answer: str = "\n".join(
        (
            f"Ваше название места: {data["name"]}",
            f"Данные о месте: {place.get_name()}\n{place.get_info()}",
            f"Ваше описание: {data["description"]}",
            f"Ваша оценка месту: {data["score"]}",
        )
    )
    await message.answer(answer)
    await custom_clear()


@router.message(NewPlaceFSM.enter_score)
async def enter_score(message: Message, state: FSMContext):
    try:
        score: int = int(message.text)
        if not (1 <= score <= 10):
            raise ScoreOutOfRange()
        await state.update_data(score=score)
        await answer_form_result(message, state)
    except ValueError:
        await message.answer("Введите число!")
    except ScoreOutOfRange:
        await message.answer("Введите число от 1 до 10")


@router.message(Command("fun"))
async def handle_cmd_fun(message: Message) -> None:
    await message.answer_animation(
        "https://media1.tenor.com/m/LWr0XvjOuo0AAAAC/pearto-pear.gif"
    )

from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from api.geosuggest.geosuggest import Geosuggest, GeosuggestResult

router = Router()


class GeosuggestTest(StatesGroup):
    enter_place = State()


@router.message(CommandStart())
async def handle_cmd_start(message: Message) -> None:
    await message.answer("Привет. Напиши /fun")


@router.message(Command("geosuggest"))
async def geosuggest_test(message: Message, state: FSMContext) -> None:
    await message.answer("Введите место для досуга: ")
    await state.set_state(GeosuggestTest.enter_place)


@router.message(GeosuggestTest.enter_place)
async def check_place(message: Message, state: FSMContext):
    responce: GeosuggestResult = Geosuggest.request(message.text)
    await message.answer(str(responce))
    await state.clear()


@router.message(Command("fun"))
async def handle_cmd_fun(message: Message) -> None:
    await message.answer_animation(
        "https://media1.tenor.com/m/LWr0XvjOuo0AAAAC/pearto-pear.gif"
    )

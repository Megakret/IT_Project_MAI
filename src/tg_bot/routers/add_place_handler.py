from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.methods.send_message import SendMessage
from aiogram.types import ReplyKeyboardRemove
from aiogram import F
import asyncio
from sqlalchemy.ext.asyncio import AsyncSession
from api.geosuggest.place import Place
from tg_bot.test_utils.comments.comments_mock import comments_mock
from tg_bot.keyboards import suggest_place_kbs, starter_kb
from tg_bot.aiogram_coros import message_sender_wrap, custom_clear
from tg_bot.ui_components.GeosuggestSelector import (
    GeosuggestSelector,
    PLACE_KEY,
    KEYBOARD_PREFIX,
)
import database.db_functions as db
from database.db_exceptions import UniqueConstraintError


class ScoreOutOfRange(Exception):
    pass


class NoTextException(Exception):
    pass


class NewPlaceFSM(StatesGroup):
    enter_place = State()
    choose_place = State()
    enter_description = State()
    enter_score = State()
    enter_comment = State()


router = Router()

geosuggest_selector = GeosuggestSelector(NewPlaceFSM.choose_place)


@router.message(CommandStart())
async def handle_cmd_start(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    await message.answer(
        "Привет. Напиши /add_place, чтобы добавить место для досуга",
        reply_markup=starter_kb,
    )
    try:
        await db.add_user(
            session, message.from_user.id, message.from_user.first_name, "blank"
        )
    except UniqueConstraintError as e:
        print(e.message)
        pass
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
    await geosuggest_selector.show_suggestions(message, state)


@router.callback_query(F.data.contains(KEYBOARD_PREFIX), NewPlaceFSM.choose_place)
async def choose_suggested_place(callback: CallbackQuery, state: FSMContext):
    await geosuggest_selector.selected_place(callback, state)
    await callback.message.answer("Введите свое описание места")
    await state.set_state(NewPlaceFSM.enter_description)


@router.message(NewPlaceFSM.enter_description)
async def enter_description(message: Message, state: FSMContext):
    description: str = message.text
    await state.update_data(description=description)
    await message.answer("Дайте оценку месту от 1 до 10")
    await state.set_state(NewPlaceFSM.enter_score)


async def answer_form_result(
    message: Message, state: FSMContext, session: AsyncSession
):
    data = await state.get_data()
    place: Place = data["place"]
    try:
        await db.add_place(
            session, place.get_name(), place.get_info(), data["description"]
        )
    except UniqueConstraintError as e:
        print("Already existing place has been tried to add to global list")
        print(e.message)
    try:
        await db.add_user_place(
            session, message.from_user.id, place.get_info(), data["score"]
        )
        answer: str = "\n".join(
            (
                f"Данные о месте: {place.get_name()}\n{place.get_info()}",
                f"Ваше описание: {data["description"]}",
                f"Ваша оценка месту: {data["score"]}",
            )
        )
        await message.answer(answer, reply_markup=starter_kb)
    except UniqueConstraintError as e:
        print(e.message)
        await message.answer("Вы уже добавляли это место", reply_markup=starter_kb)
    await custom_clear(state)


@router.message(NewPlaceFSM.enter_score)
async def enter_score(message: Message, state: FSMContext, session: AsyncSession):
    try:
        score: int = int(message.text)
        if not (1 <= score <= 10):
            raise ScoreOutOfRange()
        await state.update_data(score=score)
        await message.answer("Оставьте комментарий о месте")
        await state.set_state(NewPlaceFSM.enter_comment)
    except ValueError:
        await message.answer("Введите число!")
    except ScoreOutOfRange:
        await message.answer("Введите число от 1 до 10")


@router.message(NewPlaceFSM.enter_comment)
async def enter_comment(message: Message, state: FSMContext, session: AsyncSession):
    try:
        comment: str = message.text
        data = await state.get_data()
        place: Place = data.get("place")
        if comment == "":
            raise NoTextException
        comments_mock.add_comment(place.get_info(), comment)
        await answer_form_result(message, state, session)
    except NoTextException:
        await message.answer("Наши комментарии поддерживают только текст")


@router.message(Command("fun"))
async def handle_cmd_fun(message: Message) -> None:
    await message.answer_animation(
        "https://media1.tenor.com/m/LWr0XvjOuo0AAAAC/pearto-pear.gif"
    )

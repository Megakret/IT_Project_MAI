from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.methods.send_message import SendMessage
from aiogram.types import ReplyKeyboardRemove, KeyboardButton
from aiogram import F
from sqlalchemy.ext.asyncio import AsyncSession
from api.geosuggest.place import Place
from tg_bot.keyboards import (
    starter_admin_kb,
    starter_manager_kb,
    starter_kb,
    insert_place_tags_kb,
    INSERT_PLACE_TAGS_TAG,
)
from tg_bot.aiogram_coros import message_sender_wrap, custom_clear
from tg_bot.ui_components.GeosuggestSelector import (
    GeosuggestSelector,
    PLACE_KEY,
    KEYBOARD_PREFIX,
)
from tg_bot.ui_components.TagSelector import (
    TAGS,
    SelectTagsStates,
    show_tag_menu,
    TAG_DATA_KEY,
)
from tg_bot.tg_exceptions import NoTextMessageException, ScoreOutOfRange
import database.db_functions as db
from database.db_exceptions import UniqueConstraintError, ConstraintError
from database.db_exceptions import UniqueConstraintError
from aiogram.utils.keyboard import ReplyKeyboardBuilder


class NewPlaceFSM(StatesGroup):
    enter_place = State()
    choose_place = State()
    enter_description = State()
    enter_score = State()
    enter_comment = State()
    enter_tags = State()


async def __get_keyboard(session: AsyncSession, user_id: int):
    match await db.get_permisions(session, user_id):
        case 3:
            return starter_admin_kb
        case 2:
            return starter_manager_kb
    return starter_kb


router = Router()

geosuggest_selector = GeosuggestSelector(NewPlaceFSM.choose_place)


@router.message(CommandStart())
async def handle_cmd_start(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    try:
        await db.add_user(session, message.from_user.id, message.from_user.username)
    except UniqueConstraintError as e:
        print(e.message)
    except ConstraintError as e:
        print(e.message)
        pass
    await state.clear()
    await message.answer(
        "Привет. Напиши /add_place, чтобы добавить место для досуга",
        reply_markup=await __get_keyboard(session, message.from_user.id),
    )


@router.message(Command("exit"))
async def exit(message: Message, state: FSMContext) -> None:
    if await state.get_state() is None:
        await message.answer("Вы уже не находитесь не в каком меню")
    else:
        await message.answer("Вы вышли из текущего меню")
    await state.set_state(None)


@router.message(F.text == "Добавить место")
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
    message: Message, state: FSMContext, session: AsyncSession, comment: str
):
    data = await state.get_data()
    place: Place = data["place"]
    tags: list[str] = data.get(TAG_DATA_KEY, None)
    try:
        does_place_exist: bool = await db.is_existing_place(session, place.get_info())
        if not does_place_exist:
            await db.add_place(
                session, place.get_name(), place.get_info(), data["description"]
            )
        if tags is not None:
            await db.add_place_tags(session, place.get_info(), tuple(tags))
    except UniqueConstraintError as e:
        print("Already existing place has been tried to add to global list")
        print(e.message)
    try:
        await db.add_user_place(
            session, message.from_user.id, place.get_info(), data["score"]
        )
        await db.add_comment(session, message.from_user.id, place.get_info(), comment)
        answer: str = "\n".join(
            (
                f"Данные о месте: {place.get_name()}\n{place.get_info()}",
                f"Ваше описание: {data["description"]}",
                f"Ваша оценка месту: {data["score"]}",
            )
        )
        await message.answer(
            answer,
            reply_markup=await __get_keyboard(session, message.from_user.id),
        )
    except UniqueConstraintError as e:
        print(e.message)
        await message.answer(
            "Вы уже добавляли это место",
            reply_markup=await __get_keyboard(session, message.from_user.id),
        )
    await custom_clear(state)


@router.message(NewPlaceFSM.enter_score)
async def enter_score(message: Message, state: FSMContext):
    try:
        score: int = int(message.text)
        if not (1 <= score <= 10):
            raise ScoreOutOfRange()
        await state.update_data(score=score)
        await message.answer("Добавьте теги к месту")
        await show_tag_menu(
            message,
            state,
            keyboard=insert_place_tags_kb,
            start_message="Нажмите на тег /<tag>, чтобы добавить его к месту\n",
        )
        await state.set_state(SelectTagsStates.selecting_tag)
    except ValueError:
        await message.answer("Введите число!")
    except ScoreOutOfRange:
        await message.answer("Введите число от 1 до 10")


@router.message(NewPlaceFSM.enter_comment)
async def enter_comment(message: Message, state: FSMContext, session: AsyncSession):
    try:
        comment: str = message.text
        if comment == "":
            raise NoTextMessageException
        await answer_form_result(message, state, session, comment)
    except NoTextMessageException:
        await message.answer("Наши комментарии поддерживают только текст")


@router.callback_query(F.data == INSERT_PLACE_TAGS_TAG, SelectTagsStates.selecting_tag)
async def insert_tags(callback: CallbackQuery, state: FSMContext):
    print("BUMP")
    await callback.message.answer("Оставьте комментарий о месте")
    await state.set_state(NewPlaceFSM.enter_comment)
    await callback.answer()


@router.message(Command("fun"))
async def handle_cmd_fun(message: Message) -> None:
    await message.answer_animation(
        "https://media1.tenor.com/m/LWr0XvjOuo0AAAAC/pearto-pear.gif"
    )

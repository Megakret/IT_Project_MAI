from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from aiogram import F
from sqlalchemy.ext.asyncio import AsyncSession
from api.geosuggest.place import Place
from tg_bot.keyboards import (
    get_user_keyboard,
    insert_place_tags_kb,
    INSERT_PLACE_TAGS_TAG,
)
from tg_bot.ui_components.GeosuggestSelector import (
    GeosuggestSelector,
    KEYBOARD_PREFIX,
)
from tg_bot.ui_components.TagSelector import (
    SelectTagsStates,
    show_tag_menu,
    TAG_DATA_KEY,
)
from tg_bot.tg_exceptions import NoTextMessageException, ScoreOutOfRange
import database.db_functions as db
from database.db_exceptions import UniqueConstraintError


class NewPlaceFSM(StatesGroup):
    enter_place = State()
    choose_place = State()
    enter_description = State()
    enter_score = State()
    enter_comment = State()
    enter_tags = State()


# temp start
managers = {"NoyerXoper", "megakret"}
admins = set()


def get_permisions(user: str) -> int:
    if user in admins:
        return 2
    if user in managers:
        return 1
    return 0


# temp end


router = Router()

geosuggest_selector = GeosuggestSelector(NewPlaceFSM.choose_place)


@router.message(F.text == "Добавить место")
@router.message(Command("add_place"))
async def geosuggest_test(message: Message, state: FSMContext) -> None:
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


async def generate_final_answer(
    session: AsyncSession, database_place: db.Place, user_id: int, score: int
) -> str:
    rights_level: int = await db.get_user_rights(session, user_id)
    if rights_level > 1:
        return "\n".join(
            (
                f"Айди места: {database_place.id}",
                f"Данные о месте: {database_place.name}\n{database_place.address}",
                f"Ваше описание: {database_place.desc}",
                f"Ваша оценка месту: {score}",
            )
        )
    else:
        return "\n".join(
            (
                f"Данные о месте: {database_place.name}\n{database_place.address}",
                f"Ваше описание: {database_place.desc}",
                f"Ваша оценка месту: {score}",
            )
        )


async def answer_form_result(
    message: Message, state: FSMContext, session: AsyncSession, comment: str
):
    data = await state.get_data()
    place: Place = data["place"]
    tags: list[str] = data.get(TAG_DATA_KEY, None)
    keyboard = get_user_keyboard(session, message.from_user.id)
    address: str = place.get_info()
    try:
        does_place_exist: bool = await db.is_existing_place(session, address)
        if not does_place_exist:
            await db.add_place(session, place.get_name(), address, data["description"])
        if tags is not None:
            await db.add_place_tags(session, address, tuple(tags))
    except UniqueConstraintError as e:
        print("Already existing place has been tried to add to global list")
        print(e.message)
    try:
        await db.add_user_place(session, message.from_user.id, address, data["score"])
        await db.add_comment(session, message.from_user.id, address, comment)
        database_place: db.Place = await db.get_place_with_score(session, address)
        await message.answer(
            generate_final_answer(
                session, database_place, message.from_user.id, data["score"]
            ),
            reply_markup=keyboard,
        )
    except UniqueConstraintError as e:
        print(e.message)
        await message.answer(
            "Вы уже добавляли это место",
            reply_markup=keyboard,
        )


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
    await callback.message.answer("Оставьте комментарий о месте")
    await state.set_state(NewPlaceFSM.enter_comment)
    await callback.answer()


@router.message(Command("fun"))
async def handle_cmd_fun(message: Message) -> None:
    await message.answer_animation(
        "https://media1.tenor.com/m/LWr0XvjOuo0AAAAC/pearto-pear.gif"
    )

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import ReplyKeyboardRemove
from aiogram import F
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.routers.user_fsm import UserFSM
from api.geosuggest.place import Place
from tg_bot.keyboards import (
    get_user_keyboard,
    insert_place_tags_kb,
    yes_no_inline,
    INSERT_PLACE_TAGS_TAG,
)
from tg_bot.ui_components.GeosuggestSelector import (
    GeosuggestSelector,
    KEYBOARD_PREFIX,
)
from tg_bot.ui_components.TagSelector import (
    TagSelector,
    TAG_DATA_KEY,
)
from tg_bot.tg_exceptions import NoTextMessageException, ScoreOutOfRange
from tg_bot.filters.role_model_filters import IsAdmin, IsManager
from tg_bot.tg_exceptions import (
    NoTextMessageException,
    ScoreOutOfRange,
)
from tg_bot.filters.role_model_filters import IsAdmin, IsManager
from tg_bot.utils_and_validators import validate_message_size, MessageIsTooLarge
from tg_bot.config import MAX_COMMENT_SIZE
import database.db_functions as db
from database.db_exceptions import UniqueConstraintError


class NewPlaceFSM(StatesGroup):
    enter_place = State()
    choose_place = State()
    want_to_add_to_database = State()
    want_to_add_review = State()
    enter_description = State()
    enter_score = State()
    enter_comment = State()
    select_tags = State()


router = Router()

geosuggest_selector = GeosuggestSelector(NewPlaceFSM.choose_place)
tag_selector = TagSelector(selecting_state=NewPlaceFSM.select_tags, router=router)


@router.message(F.text == "Добавить место", UserFSM.start_state)
@router.message(Command("add_place"), UserFSM.start_state)
async def geosuggest_test(message: Message, state: FSMContext) -> None:
    await message.answer(
        "Чтобы выйти из команды, напишите /exit. Введите место для досуга: ",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(NewPlaceFSM.enter_place)


@router.message(NewPlaceFSM.enter_place, F.text)
async def show_suggestions(message: Message, state: FSMContext):
    await geosuggest_selector.show_suggestions(message, state)


@router.callback_query(F.data.contains(KEYBOARD_PREFIX), NewPlaceFSM.choose_place)
async def check_place_existence_handler(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await geosuggest_selector.selected_place(callback, state)
    data = await state.get_data()
    place: Place = data["place"]
    place_exists_in_base: bool = await db.is_existing_place(session, place.get_info())
    place_added_by_user: bool = await db.is_existing_user_place(
        session, place.get_info(), callback.from_user.id
    )
    if place_added_by_user:
        await callback.message.answer(
            "Вы уже добавляли это место",
            reply_markup=await get_user_keyboard(session, callback.from_user.id),
        )
        await state.set_state(UserFSM.start_state)
    elif place_exists_in_base:
        await callback.message.answer(
            "Хотите оставить отзыв на место?", reply_markup=yes_no_inline
        )
        await state.set_state(NewPlaceFSM.want_to_add_review)
    else:
        await callback.message.answer(
            "Этого места еще нет в нашей базе мест. Хотите отправить запрос менеджеру на его добавление?",
            reply_markup=yes_no_inline,
        )
        await state.set_state(NewPlaceFSM.want_to_add_to_database)
        print("got here")


@router.callback_query(F.data == "yes", NewPlaceFSM.want_to_add_to_database)
async def user_wants_to_add_desc_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Отлично. Введите описание места.", reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(NewPlaceFSM.enter_description)
    await callback.answer()


@router.callback_query(NewPlaceFSM.want_to_add_to_database, F.data == "no")
async def user_dont_want_to_add_desc_handler(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await state.set_state(UserFSM.start_state)
    await callback.message.answer(
        "Место не было добавлено в ваш список",
        reply_markup=await get_user_keyboard(session, callback.from_user.id),
    )
    await callback.answer()


@router.message(NewPlaceFSM.enter_description, F.text)
async def enter_description_handler(message: Message, state: FSMContext):
    description: str = message.text
    await state.update_data(description=description)
    await tag_selector.show_tag_menu(
        message,
        state,
        keyboard=insert_place_tags_kb,
        start_message="Нажмите на тег /<tag>, чтобы добавить его к месту\n",
    )


@router.message(NewPlaceFSM.enter_description)
async def enter_description_handler(message: Message, state: FSMContext):
    await message.answer("Описание должно содержать только текст!")


# for now it just adds place. easy to fix when db will be ready
@router.callback_query(NewPlaceFSM.select_tags, F.data == INSERT_PLACE_TAGS_TAG)
async def add_request_to_manager(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    data = await state.get_data()
    try:
        place: Place = data["place"]
        tags: list[str] = data[TAG_DATA_KEY]
        await db.add_place(
            session, place.get_name(), place.get_info(), data["description"]
        )
        await db.add_place_tags(session, place.get_info(), tags)
        await callback.answer("Место успешно добавлено")
        await callback.message.answer(
            "Хотите добавить отзыв на место?", reply_markup=yes_no_inline
        )
        await state.set_state(NewPlaceFSM.want_to_add_review)
    except KeyError:
        await state.clear()
        await callback.answer("Что-то пошло не так, попробуйте ввести команду снова")
    except UniqueConstraintError as e:
        print(e.message)
        await state.set_state(UserFSM.start_state)
        await callback.answer(
            "Извините, похоже, пока вы добавляли место, кто-то другой добавил его быстрее вас."
        )


@router.callback_query(NewPlaceFSM.want_to_add_review, F.data == "yes")
async def want_to_add_review_handler(callback: CallbackQuery, state: FSMContext):
    await callback.message.answer(
        "Введите свою оценку месту от 1 до 10.", reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(NewPlaceFSM.enter_score)


@router.message(NewPlaceFSM.enter_score, F.text)
async def enter_score_handler(message: Message, state: FSMContext):
    try:
        score: int = int(message.text)
        if not (1 <= score <= 10):
            raise ScoreOutOfRange
        await state.update_data(score=score)
        await state.set_state(NewPlaceFSM.enter_comment)
        await message.answer("Напишите комментарий для своего отзыва")
    except ValueError:
        await message.answer("Вы ввели не число, либо дробное число!")
    except ScoreOutOfRange:
        await message.answer("Вы должны ввести оценку от 1 до 10!")


@router.message(NewPlaceFSM.enter_comment, F.text)
async def enter_comment_handler(
    message: Message, state: FSMContext, session: AsyncSession
):
    try:
        comment: str = validate_message_size(message.text, MAX_COMMENT_SIZE)
        await state.update_data(comment=comment)
        await add_user_place_with_feedback(
            message, state, session, message.from_user.id
        )
    except MessageIsTooLarge as e:
        print(e)
        await message.answer(
            f"В вашем комментарие слишком много символов: {e.message_size}."
            f"Максимальное количество символов: {e.max_size}"
        )


@router.message(NewPlaceFSM.enter_comment)
async def wrong_comment_handler(message: Message):
    await message.answer("Вы можете оставить только текстовый комментарий.")


@router.callback_query(NewPlaceFSM.want_to_add_review, F.data == "no")
async def dont_want_to_add_review_handler(
    callback: CallbackQuery, session: AsyncSession, state: FSMContext
):
    await add_user_place_with_feedback(
        callback.message, state, session, callback.from_user.id
    )
    await callback.answer()


async def generate_final_answer(
    session: AsyncSession, database_place: db.Place, user_id: int, score: int | None
) -> str:
    rights_level: int = await db.get_user_rights(session, user_id)
    if rights_level > 1:
        if score is None:
            return "\n".join(
                (
                    f"Айди места: {database_place.id}",
                    f"Данные о месте: {database_place.name}\n{database_place.address}",
                    f"Описание места: {database_place.desc}",
                )
            )

        return "\n".join(
            (
                f"Айди места: {database_place.id}",
                f"Данные о месте: {database_place.name}\n{database_place.address}",
                f"Описание места: {database_place.desc}",
                f"Ваша оценка месту: {score}",
            )
        )
    else:
        if score is None:
            return "\n".join(
                (
                    f"Данные о месте: {database_place.name}\n{database_place.address}",
                    f"Описание места: {database_place.desc}",
                )
            )
        return "\n".join(
            (
                f"Данные о месте: {database_place.name}\n{database_place.address}",
                f"Описание места: {database_place.desc}",
                f"Ваша оценка месту: {score}",
            )
        )


async def add_user_place_with_feedback(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user_id: int,
):
    data = await state.get_data()
    place: Place = data["place"]
    keyboard = await get_user_keyboard(session, user_id)
    address: str = place.get_info()
    comment: str | None = data.get("comment", None)
    score: int | None = data.get("score", None)
    try:
        await db.add_user_place(session, user_id, address, score, comment)
        database_place: db.Place = (await db.get_place_with_score(session, address))[0]
        await message.answer(
            await generate_final_answer(session, database_place, user_id, score),
            reply_markup=keyboard,
        )
    except UniqueConstraintError as e:
        print(e.message)
        await message.answer(
            "Вы уже добавляли это место",
            reply_markup=keyboard,
        )
    await state.set_state(UserFSM.start_state)


@router.message(Command("fun"))
async def handle_cmd_fun(message: Message) -> None:
    await message.answer_animation(
        "https://media1.tenor.com/m/LWr0XvjOuo0AAAAC/pearto-pear.gif"
    )

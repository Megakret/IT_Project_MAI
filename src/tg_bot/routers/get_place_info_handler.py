from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from aiogram.fsm.state import State, StatesGroup

from tg_bot.routers.user_fsm import UserFSM
from tg_bot.ui_components.GeosuggestSelector import (
    GeosuggestSelector,
    KEYBOARD_PREFIX,
    PLACE_KEY,
)
from tg_bot.ui_components.Paginator import PaginatorService
from tg_bot.tg_exceptions import ScoreOutOfRange
from api.geosuggest.place import Place
from api.gpt.GptSummarize import GptSummarize
from api.gpt.GptRetellingDescription import GptRetellingDescription
import database.db_functions as db
from database.db_exceptions import UniqueConstraintError
from tg_bot.keyboards import (
    show_comments_keyboard,
    GET_COMMENTS_TAG,
    NEXT_PAGE,
    PREV_PAGE,
    INDICATOR_CLICKED,
    SUMMARIZE_COMMENTS_TAG,
    LEAVE_COMMENT_TAG,
    SUMMARIZE_DESCRIPTION_TAG,
)
from tg_bot.utils_and_validators import MessageIsTooLarge, validate_message_size
from tg_bot.config import MAX_COMMENT_SIZE


router = Router()
POSTFIX = "comments"


class NoPlaceException(Exception):
    pass


class NoComments(Exception):
    pass


class GetPlaceStates(StatesGroup):
    enter_place = State()
    choose_place = State()
    enter_score = State()
    enter_comment = State()


async def get_comments_for_paginator(
    page: int, places_per_page: int, address: str, session: AsyncSession
) -> list[str]:
    usernames_comments_scores: list[tuple[str, str, int]] = await db.get_place_comments(
        session, page, places_per_page, address
    )
    if usernames_comments_scores is None:
        return []
    paged_data: list[str] = map(
        lambda x: f"{x[0]}\n{x[1]}\nОценка месту: {x[2]}", usernames_comments_scores
    )
    return list(paged_data)


geosuggest_selector = GeosuggestSelector(GetPlaceStates.choose_place)
paginator_service = PaginatorService(
    POSTFIX, 5, get_comments_for_paginator, "Пока что для этого места нет комментариев"
)


@router.message(F.text == "Найти место", UserFSM.start_state)
@router.message(Command("get_place"), UserFSM.start_state)
async def get_place_handler(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer(
        "Чтобы выйти из команды, напишите /exit. Введите название места:"
    )
    await state.set_state(GetPlaceStates.enter_place)
    try:
        await paginator_service.update_paginator(
            state, "Достопримечательность · Калининград, Ленинградский район", session
        )
    except:
        pass


@router.message(GetPlaceStates.enter_place, F.text)
async def enter_place_handler(message: Message, state: FSMContext):
    await geosuggest_selector.show_suggestions(message, state)


async def generate_place_answer(
    session: AsyncSession, db_place: db.Place, score: int | None, user_id: int
) -> str:
    user_rights: int = await db.get_user_rights(session, user_id)
    answer = ""
    if user_rights > 1:
        answer += f"Айди места: {db_place.id}\n"
    if score is None:
        return answer + (
            f"{db_place.name}\n{db_place.address}\n{db_place.desc}\nВы пока не оценили это место"
        )
    else:
        return answer + (
            f"{db_place.name}\n{db_place.address}\n{db_place.desc}\nВаша оценка месту: {score}"
        )


@router.callback_query(F.data.contains(KEYBOARD_PREFIX), GetPlaceStates.choose_place)
async def find_place_handler(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await geosuggest_selector.selected_place(callback, state)
    data = await state.get_data()
    place: Place = data.get(PLACE_KEY)
    try:
        db_res = await db.get_place_with_score(session, place.get_info())
        db_place: db.Place = db_res[0]
        score: int | None = db_res[1]
        await state.update_data(description=db_place.desc)
        await callback.message.answer(
            await generate_place_answer(
                session, db_place, score, callback.from_user.id
            ),
            reply_markup=show_comments_keyboard,
        )
    except NoResultFound:
        await callback.message.answer(
            "Этого места еще нет в базе, но вы можете его добавить с помощью команды /add_place"
        )


@router.callback_query(F.data == GET_COMMENTS_TAG, GetPlaceStates.choose_place)
async def show_comments(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    try:
        data: dict[str, any] = await state.get_data()
        place: Place = data.get(PLACE_KEY)
        if place is None:
            raise NoPlaceException
        await paginator_service.start_paginator(
            callback.message, state, place.get_info(), session
        )
        await callback.answer()
    except NoPlaceException:
        await callback.answer("Попробуйте ввести место еще раз")


@router.callback_query(F.data == NEXT_PAGE + POSTFIX, GetPlaceStates.choose_place)
async def next_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    try:
        data: dict[str, any] = await state.get_data()
        place: Place = data.get(PLACE_KEY)
        if place is None:
            raise NoPlaceException
        await paginator_service.show_next_page(
            callback, state, place.get_info(), session
        )
    except NoPlaceException:
        await callback.answer("Попробуйте ввести место еще раз")


@router.callback_query(F.data == PREV_PAGE + POSTFIX, GetPlaceStates.choose_place)
async def next_page(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    try:
        data: dict[str, any] = await state.get_data()
        place: Place = data.get(PLACE_KEY)
        if place is None:
            raise NoPlaceException
        await paginator_service.show_prev_page(
            callback, state, place.get_info(), session
        )
    except NoPlaceException:
        await callback.answer("Попробуйте ввести место еще раз")


@router.callback_query(
    F.data == INDICATOR_CLICKED + POSTFIX, GetPlaceStates.choose_place
)
async def indicator_clicked(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    try:
        data: dict[str, any] = await state.get_data()
        place: Place = data.get(PLACE_KEY)
        if place is None:
            raise NoPlaceException
        await paginator_service.indicator_clicked(
            callback, state, place.get_info(), session
        )
    except NoPlaceException:
        await callback.answer("Попробуйте ввести место еще раз")


@router.callback_query(F.data == SUMMARIZE_COMMENTS_TAG, GetPlaceStates.choose_place)
async def summarize_comments(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    try:
        data: dict[str, any] = await state.get_data()
        place: Place = data.get(PLACE_KEY)
        if place is None:
            raise NoPlaceException
        await callback.answer("Ожидайте...")
        summarizer = GptSummarize()
        comments = await db.get_place_comments_all(session, place.get_info())
        if len(comments) == 0:
            raise NoComments
        summarization: str = await summarizer.summarize_NAC(comments)
        await callback.message.answer(summarization)
        await callback.answer()
    except NoPlaceException:
        await callback.answer("Попробуйте ввести место еще раз")
    except NoComments:
        await callback.answer("Пока что для этого места нет комментариев")


@router.callback_query(F.data == LEAVE_COMMENT_TAG, GetPlaceStates.choose_place)
async def pressed_leave_comment_button(callback: CallbackQuery, state: FSMContext):
    try:
        data = await state.get_data()
        place: Place = data.get(PLACE_KEY)
        if place is None:
            raise NoPlaceException
        await callback.message.answer("Оцените место от 1 до 10")
        await callback.answer()
        await state.set_state(GetPlaceStates.enter_score)
    except NoPlaceException:
        await callback.answer("Попробуйте ввести место еще раз")


@router.message(GetPlaceStates.enter_score, F.text)
async def enter_score(message: Message, state: FSMContext):
    try:
        score: int = int(message.text)
        if not (1 <= score <= 10):
            raise ScoreOutOfRange
        await state.update_data(score=score)
        await state.set_state(GetPlaceStates.enter_comment)
        await message.answer("Напишите комментарий к месту")
    except ValueError:
        await message.answer("Вы ввели не число, либо дробное число!")
    except ScoreOutOfRange:
        await message.answer("Вы должны ввести оценку от 1 до 10!")


@router.message(GetPlaceStates.enter_comment, F.text)
async def enter_comment(message: Message, state: FSMContext, session: AsyncSession):
    try:
        comment = validate_message_size(message.text, MAX_COMMENT_SIZE)
        data = await state.get_data()
        place: Place | None = data.get(PLACE_KEY)
        score: int | None = data.get("score")
        if place is None:
            raise NoPlaceException
        try:
            await db.add_user_place(
                session, message.from_user.id, address=place.get_info(), score=score, comment=comment
            )  # adding user place by default so comment will save
        except UniqueConstraintError as e:
            print(e)
            pass
        await db.rate(session, message.from_user.id, place.get_info(), score)
        await db.add_comment(session, message.from_user.id, place.get_info(), comment)
        await message.answer("Ваш комментарий успешно добавлен")
        await state.set_state(GetPlaceStates.choose_place)
    except NoPlaceException:
        await message.answer("Попробуйте ввести место еще раз")
    except MessageIsTooLarge as e:
        print(e)
        await message.answer(
            f"В вашем комментарие слишком много символов: {e.message_size}."
            f"Максимальное количество символов: {e.max_size}"
        )


@router.callback_query(F.data == SUMMARIZE_DESCRIPTION_TAG, GetPlaceStates.choose_place)
async def summarize_description(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    try:
        description: str = data["description"]
        reteller = GptRetellingDescription()
        await callback.answer("Ожидайте...")
        summarization: str = await reteller.retell_nac(description)
        await callback.message.answer(summarization)
    except KeyError:
        await callback.answer("Что-то пошло не так. Напишите команду заново.")

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    CallbackQuery,
)

from tg_bot.routers.admin_ui.user_manipulation.functions import validate_username
from tg_bot.keyboards import (
    select_comment_deletion_mode_kb,
    NEXT_PAGE,
    PREV_PAGE,
    INDICATOR_CLICKED,
)
from tg_bot.routers.role_model_fsm.admin_fsm import AdminFSM, UserManipulationFSM
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from tg_bot.config import BOT_USERNAME
from tg_bot.ui_components.Paginator import PaginatorService
from tg_bot.ui_components.GeosuggestSelector import (
    GeosuggestSelector,
    KEYBOARD_PREFIX,
    PLACE_KEY,
)
import database.db_functions as db

router = Router()
COMMENTS_PER_PAGE_FOR_DELETION = 4
POSTFIX_COMMENTS = "comments_manager"


async def get_comments(
    page: int,
    comments_per_page: int,
    session: AsyncSession,
    address: str | None = None,
    username: str | None = None,
    *args,
    **kwargs,
):
    if address:
        comments = await db.get_place_comments(
            session, page, comments_per_page, address
        )
        id: list[db.Place, str, int] = (
            await db.get_place_with_score(session, address)
        )[0].id
        return [
            f'@{username}\n{comment}\nОцена:{score if score else "Без оценки"}\n<a href="https://t.me/{BOT_USERNAME}?text=/delete+{id}+{username}">Удалить комментарий</a>'
            for username, comment, score in comments
        ]
    elif username:
        comments = await db.get_comments_of_user(
            session, page, comments_per_page, username
        )
        return [
            f'@{username}\n{place_data.name}\n{place_data.address}\n\n{comment}\nОцена: {score if score else "Без оценки"}\n<a href="https://t.me/{BOT_USERNAME}?text=/delete+{place_data.id}+{username}">Удалить комментарий</a>'
            for place_data, comment, score in comments
        ]
    raise ValueError("Username and address are None at the same time.")


delete_comments_paginator_service = PaginatorService(
    POSTFIX_COMMENTS,
    COMMENTS_PER_PAGE_FOR_DELETION,
    get_comments,
    "В базе данных пока нет комментариев по данному критерию",
)

geosuggest_for_place = GeosuggestSelector(
    UserManipulationFSM.select_place_for_comment_deletion
)


@router.message(F.text == "Удаление комментариев", AdminFSM.user_manipulation_state)
async def delete_comments(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer(
        "Выберите то, как Вы хотите просматривать комментарии",
        reply_markup=select_comment_deletion_mode_kb,
    )
    await state.set_state(UserManipulationFSM.choose_mode_for_deletion)


@router.message(
    F.text == "Поиск по месту", UserManipulationFSM.choose_mode_for_deletion
)
async def search_by_place(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer("Введите название места:")
    await state.set_state(UserManipulationFSM.delete_comments_place_input)


@router.message(UserManipulationFSM.delete_comments_place_input)
async def geosuggest_show(message: Message, state: FSMContext):
    await geosuggest_for_place.show_suggestions(message, state)
    await state.set_state(UserManipulationFSM.select_place_for_comment_deletion)


@router.callback_query(
    F.data.contains(KEYBOARD_PREFIX),
    UserManipulationFSM.select_place_for_comment_deletion,
)
async def choose_place_action(
    call: CallbackQuery, state: FSMContext, session: AsyncSession
):
    print("Place selected")
    await geosuggest_for_place.selected_place(call, state)
    data = await state.get_data()
    place: db.Place = data.get(PLACE_KEY)
    try:
        db_res = await db.get_place_with_score(session, place.get_info())
    except NoResultFound:
        await call.message.answer("Этого места еще нет в базе данных")
        return
    await state.set_state(UserManipulationFSM.delete_comments_paginator_state)
    await state.update_data({"username": None, "address": db_res[0].address})
    await delete_comments_paginator_service.start_paginator(
        call.message, state, session, address=db_res[0].address, parse_mode="HTML"
    )


@router.message(
    F.text == "Поиск по пользователю", UserManipulationFSM.choose_mode_for_deletion
)
async def search_by_username(
    message: Message, state: FSMContext, session: AsyncSession
):
    await message.answer(
        "Введите имя пользователя через @:", reply_markup=ReplyKeyboardRemove()
    )
    await state.set_state(UserManipulationFSM.delete_comments_name_input)


@router.message(UserManipulationFSM.delete_comments_name_input)
async def search_username(message: Message, state: FSMContext, session: AsyncSession):
    text = message.text.strip()
    if not validate_username(text):
        await message.answer(
            "Введён неверный формат имени. Используйте /exit для выхода"
        )
        return
    if not await db.does_user_exist(session, text[1:]):
        await message.answer("Данный пользователь не найдён")
        return
    await state.set_state(UserManipulationFSM.delete_comments_paginator_state)
    await state.update_data({"username": text[1:], "address": None})
    await delete_comments_paginator_service.start_paginator(
        message, state, session, username=text[1:], parse_mode="HTML"
    )


@router.callback_query(F.data == NEXT_PAGE + POSTFIX_COMMENTS)
async def next_comments_page(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await delete_comments_paginator_service.show_next_page(
        callback, state, session, **(await state.get_data()), parse_mode="HTML"
    )


@router.callback_query(F.data == PREV_PAGE + POSTFIX_COMMENTS)
async def prev_comments_page(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await delete_comments_paginator_service.show_prev_page(
        callback, state, session, **(await state.get_data()), parse_mode="HTML"
    )


@router.callback_query(F.data == INDICATOR_CLICKED + POSTFIX_COMMENTS)
async def indicator_clicked_comments(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    print("indicator clicked")
    data = await state.get_data()
    await delete_comments_paginator_service.indicator_clicked(
        callback,
        state,
        session,
        username=data["username"],
        address=data["address"],
        parse_mode="HTML",
    )


@router.message(Command("delete"), UserManipulationFSM.delete_comments_paginator_state)
async def delete_comment(message: Message, state: FSMContext, session: AsyncSession):
    id, username = message.text[len("/delete ") :].split()
    id = int(id)
    data = await state.get_data()
    print(data["username"])
    await message.delete()
    try:
        await db.remove_review(session, username, id)
        await delete_comments_paginator_service.update_paginator(
            state,
            session,
            parse_mode="HTML",
            username=data["username"],
            address=data["address"],
        )
    except:
        await message.answer(
            "Не получилось удалить комментарий, вероятно, другой админ уже удалил его - перезагрузите страницу, нажав на номер страницы"
        )
        return

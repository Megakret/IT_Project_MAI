from tg_bot.DispatcherHandler import DispatcherHandler
from aiogram import F, Router, Bot
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command, or_f
from aiogram.types import (
    Message,
    ReplyKeyboardRemove,
    CallbackQuery,
)

from tg_bot.keyboards import (
    yes_no_inline,
    set_role_inline,
    set_role_owner_inline,
    user_manipulation_admin_kb,
    chose_role_for_paginator_inline,
    back_kb,
    select_comment_deletion_mode_kb,
    NEXT_PAGE,
    PREV_PAGE,
    INDICATOR_CLICKED,
)
from tg_bot.routers.role_model_fsm.admin_fsm import AdminFSM, UserManipulationFSM
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound

from tg_bot.ui_components.Paginator import PaginatorService
from tg_bot.ui_components.GeosuggestSelector import (
    GeosuggestSelector,
    KEYBOARD_PREFIX,
    PLACE_KEY,
)
import database.db_functions as db

router = Router()
PLACES_PER_PAGE_USERS = 5
COMMENTS_PER_PAGE_FOR_DELETION = 4
POSTFIX_USERS = "list_of_users"
POSTFIX_COMMENTS = "comments_manager"


def validate_username(tag: str) -> bool:
    return (
        tag.startswith("@")
        and tag.isascii()
        and len(set(" ,.:/!\\\"'?") & set(tag)) == 0
    )


async def get_formatted_list(
    page: int,
    places_per_page: int,
    session: AsyncSession,
    permission: int,
    *args,
    **kwargs,
) -> list[str]:
    if permission:
        users_list: list[str] = await db.get_users_by_permission(
            session, page, places_per_page, permission
        )
    else:
        users_list: list[str] = await db.get_banned_users(
            session, page, places_per_page
        )
    users_formated = map(lambda x: f"`@{x}`", users_list)
    return list(users_formated)


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
            f"@{username}\n{comment}\nОцена:{score}\n[Удалить комментарий](https://t.me/BulkovBot?text=/delete+{id}+{username})"
            for username, comment, score in comments
        ]
    elif username:
        comments = await db.get_comments_of_user(
            session, page, comments_per_page, username
        )
        return [
            f"@{username}\n{place_data.name}\n{place_data.address}\n\n{comment}\nОцена:{score}\n[Удалить комментарий](https://t.me/BulkovBot?text=/delete+{place_data.id}+{username})"
            for place_data, comment, score in comments
        ]
    raise ValueError("None and None")


paginator_service = PaginatorService(
    POSTFIX_USERS,
    PLACES_PER_PAGE_USERS,
    get_formatted_list,
    "В базе данных пока нет ни пользователя с заданными правами",
)

delete_comments_paginator_service = PaginatorService(
    POSTFIX_COMMENTS,
    COMMENTS_PER_PAGE_FOR_DELETION,
    get_comments,
    "В базе данных пока нет комментариев по данному критерию",
)

geosuggest_for_place = GeosuggestSelector(
    UserManipulationFSM.select_place_for_comment_deletion
)


@router.message(F.text == "Управление пользователями", AdminFSM.start_state)
async def open_menu(message: Message, state: FSMContext):
    await state.set_state(AdminFSM.user_manipulation_state)
    await message.answer(
        "Вы вошли в меню управления пользователями.",
        reply_markup=user_manipulation_admin_kb,
    )


@router.message(Command("exit"), or_f(*UserManipulationFSM.__all_states__))
@router.message(F.text == "Назад", UserManipulationFSM.choose_role_for_paginator_state)
async def exit_to_first_menu(message: Message, state: FSMContext):
    await message.answer(
        "Переход в меню управления пользователями...",
        reply_markup=user_manipulation_admin_kb,
    )
    await state.clear()
    await state.set_state(AdminFSM.user_manipulation_state)


@router.message(F.text == "Список пользователей", AdminFSM.user_manipulation_state)
async def show_users_by_permission(
    message: Message, state: FSMContext, session: AsyncSession
):
    message_to_delete = await message.answer("Загрузка...", reply_markup=back_kb)
    await message.answer(
        "Выберите роль для показа:", reply_markup=chose_role_for_paginator_inline
    )
    # await message_to_delete.delete()
    await state.set_state(UserManipulationFSM.choose_role_for_paginator_state)


@router.callback_query(
    F.data == "banned", UserManipulationFSM.choose_role_for_paginator_state
)
async def show_banned(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.start_paginator_on_message(
        call.message, state, session, 0, parse_mode="MARKDOWN"
    )
    await call.message.answer(
        "Возвращение в меню управления пользователями",
        reply_markup=user_manipulation_admin_kb,
    )
    await state.set_state(AdminFSM.user_manipulation_state)


@router.callback_query(
    F.data == "user", UserManipulationFSM.choose_role_for_paginator_state
)
async def show_banned(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.start_paginator_on_message(
        call.message, state, session, 1, parse_mode="MARKDOWN"
    )
    await call.message.answer(
        "Возвращение в меню управления пользователями",
        reply_markup=user_manipulation_admin_kb,
    )
    await state.set_state(AdminFSM.user_manipulation_state)


@router.callback_query(
    F.data == "manager", UserManipulationFSM.choose_role_for_paginator_state
)
async def show_banned(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.start_paginator_on_message(
        call.message, state, session, 2, parse_mode="MARKDOWN"
    )
    await call.message.answer(
        "Возвращение в меню управления пользователями",
        reply_markup=user_manipulation_admin_kb,
    )
    await state.set_state(AdminFSM.user_manipulation_state)


@router.callback_query(
    F.data == "admin", UserManipulationFSM.choose_role_for_paginator_state
)
async def show_admin(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    await paginator_service.start_paginator_on_message(
        call.message, state, session, 3, parse_mode="MARKDOWN"
    )
    await call.message.answer(
        "Возвращение в меню управления пользователями",
        reply_markup=user_manipulation_admin_kb,
    )
    await state.set_state(AdminFSM.user_manipulation_state)


@router.message(F.text == "Забанить пользователя", AdminFSM.user_manipulation_state)
async def ban_start(message: Message, state: FSMContext):
    await message.answer(
        "Введите имя пользователя человека, которого Вы хотите заблокировать.\nДля выхода пропишите /exit",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(UserManipulationFSM.ban_state)


@router.message(UserManipulationFSM.ban_state)
async def ban_input(message: Message, state: FSMContext, session: AsyncSession):
    text = message.text.strip()
    if text[1:] == message.from_user.username:
        await message.answer("Не стоит себя блокировать.\nДля выхода пропишите /exit")
        return
    if not validate_username(text):
        await message.answer(
            "Формат имени пользователя неверен. Для выхода пропишите /exit"
        )
        return
    if not await db.does_user_exist(session, text[1:]):
        await message.answer(
            f"Пользователь {text} не найден.\nДля выхода пропишите /exit"
        )
        return
    if not await db.is_owner(session, message.from_user.id) and await db.is_admin(
        session, await db.get_id_by_username(session, text[1:])
    ):
        await message.answer(
            f"Только владелец может блокировать админов.\nДля выхода пропишите /exit"
        )
        return
    if await db.is_username_banned(session, text[1:]):
        await message.answer(
            f"Пользователь {text} уже заблокирован.\nДля выхода пропишите /exit"
        )
        return

    await state.set_state(UserManipulationFSM.ban_verify_state)
    await state.set_data({"username": text})
    await message.answer(
        f"Хотите ли Вы забанить пользователя с ником {text}?\nВсе его права будут удалены.",
        reply_markup=yes_no_inline,
    )


@router.callback_query(F.data == "yes", UserManipulationFSM.ban_verify_state)
async def delete_data_of_banned_person_verify(
    call: CallbackQuery, state: FSMContext, session: AsyncSession
):
    username: str = (await state.get_data())["username"]
    try:
        await db.ban_by_username(session, username[1:])
    except:
        await call.message.answer(
            "Вероятно, вы ошиблись в нике пользователя. Попробуйте ещё раз ввести. Для выхода пропишите /exit"
        )
        await state.set_state(UserManipulationFSM.ban_state)
    id = await db.get_id_by_username(session, username[1:])
    await call.message.edit_text(
        f"Пользователь {username} забанен.\nХотите ли вы удалить данные о нём?",
        reply_markup=yes_no_inline,
    )
    await DispatcherHandler.send_message(
        id, "Поздравляем, Вы забанены!", reply_markup=ReplyKeyboardRemove()
    )
    await DispatcherHandler.set_state(id, None)
    await state.set_state(UserManipulationFSM.deletion_state)
    await call.answer()


@router.callback_query(F.data == "no", UserManipulationFSM.ban_verify_state)
async def not_banned(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "Пользователь не был забанен. Возвращение в меню",
        reply_markup=user_manipulation_admin_kb,
    )
    await state.clear()
    await state.set_state(AdminFSM.user_manipulation_state)
    await call.answer()


@router.callback_query(F.data == "yes", UserManipulationFSM.deletion_state)
async def delete_data(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    username: str = (await state.get_data())["username"]
    await db.delete_user_data_by_username(session, username[1:])
    await call.message.answer(
        "Данные пользователя удалены", reply_markup=user_manipulation_admin_kb
    )
    await state.clear()
    await state.set_state(AdminFSM.user_manipulation_state)
    await call.answer()


@router.callback_query(F.data == "no", UserManipulationFSM.deletion_state)
async def banned_without_deletion(call: CallbackQuery, state: FSMContext):
    await call.message.answer(
        "Пользователь забанен, но его данные сохранены",
        reply_markup=user_manipulation_admin_kb,
    )
    await state.clear()
    await state.set_state(AdminFSM.user_manipulation_state)
    await call.answer()


@router.message(F.text == "Разбанить пользователя", AdminFSM.user_manipulation_state)
async def unban(message: Message, state: FSMContext, session: AsyncSession):
    await message.answer(
        "Введите имя пользователя, которого вы хотите разблокировать.\nДля выходи пропишите /exit\nСписок заблокированных пользователей:",
        reply_markup=ReplyKeyboardRemove(),
    )
    await paginator_service.start_paginator(
        message, state, session, 0, parse_mode="MARKDOWN"
    )
    await state.set_state(UserManipulationFSM.unban_name_input_state)


@router.message(UserManipulationFSM.unban_name_input_state)
async def unban_person(message: Message, state: FSMContext, session: AsyncSession):
    text = message.text.strip()
    if not validate_username(text):
        await message.answer("Неправильный формат имени, для выходи пропишите /exit")
        return
    if not await db.is_username_banned(session, text[1:]):
        await message.answer(
            f"Пользователь {text} либо не заблокирован, либо не существует"
        )
        return
    await db.unban_by_username(session, message.text[1:])
    await message.answer(
        f"Пользователь {text} разблокирован",
        reply_markup=user_manipulation_admin_kb,
    )
    await state.set_state(AdminFSM.user_manipulation_state)


@router.message(
    F.text == "Изменить роль пользователя", AdminFSM.user_manipulation_state
)
async def change_role(message: Message, state: FSMContext):
    await message.answer(
        "Введите имя пользователя через @\nДля выхода пропишите /exit",
        reply_markup=ReplyKeyboardRemove(),
    )
    await state.set_state(UserManipulationFSM.change_role_state)


@router.message(UserManipulationFSM.change_role_state)
async def change_role_input_name(
    message: Message, state: FSMContext, session: AsyncSession
):
    if message.text[1:] == message.from_user.username:
        await message.answer(
            "Вы не можете изменить свою собственную роль!\nДля выхода пропишите /exit"
        )
        return
    if not validate_username(message.text):
        await message.answer(
            f"Неверный формат имени: `{message.text}`. Для выхода пропишите /exit",
            parse_mode="MARKDOWN",
        )
        return
    if not (await db.does_user_exist(session, message.text[1:])):
        await message.answer(
            f"Пользователь `{message.text}` не существует. Для выхода пропишите /exit",
            parse_mode="MARKDOWN",
        )
        return
    if await db.is_username_banned(session, message.text[1:]):
        await message.answer(
            f"Пользователь `{message.text}` заблокирован. Для выхода пропишите /exit",
            parse_mode="MARKDOWN",
        )
        return
    is_it_owner = await db.is_owner(session, message.from_user.id)
    is_targert_admin = await db.is_admin(
        session, await db.get_id_by_username(session, message.text[1:])
    )
    if not is_it_owner and is_targert_admin:
        await message.answer(
            "Только владельцы могут менять роли админов! Для выхода пропишите /exit"
        )
        return
    if is_it_owner:
        await message.answer("Выберите роль:", reply_markup=set_role_owner_inline)
        await state.update_data({"is_owner": True, "username": message.text})
        await state.set_state(UserManipulationFSM.select_role_state)
    else:
        await message.answer("Выберите роль:", reply_markup=set_role_inline)
        await state.update_data({"is_owner": False, "username": message.text})
        await state.set_state(UserManipulationFSM.select_role_state)


@router.callback_query(F.data == "user", UserManipulationFSM.select_role_state)
async def set_user(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await db.make_user(session, data["username"][1:])
    await call.message.answer(
        f'{data["username"]} теперь имеет роль "Пользователь"',
        reply_markup=user_manipulation_admin_kb,
    )
    await state.set_state(AdminFSM.user_manipulation_state)
    await call.answer()


@router.callback_query(F.data == "manager", UserManipulationFSM.select_role_state)
async def set_manager(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    await db.make_manager(session, data["username"][1:])
    await call.message.answer(
        f'{data["username"]} теперь имеет роль "Менеджер"',
        reply_markup=user_manipulation_admin_kb,
    )
    await state.set_state(AdminFSM.user_manipulation_state)
    await call.answer()


@router.callback_query(F.data == "admin", UserManipulationFSM.select_role_state)
async def set_admin(call: CallbackQuery, state: FSMContext, session: AsyncSession):
    data = await state.get_data()
    if not data["is_owner"]:
        await call.message.answer("А твикать коллбеки не красиво, ничего не получилось")
        return
    await db.make_admin(session, data["username"][1:])
    await call.message.answer(
        f'{data["username"]} теперь имеет роль "Админ"',
        reply_markup=user_manipulation_admin_kb,
    )
    await state.set_state(AdminFSM.user_manipulation_state)
    await call.answer()


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
        call.message, state, session, address=db_res[0].address, parse_mode="MARKDOWN"
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
        message, state, session, username=text[1:], parse_mode="MARKDOWN"
    )


@router.callback_query(F.data == NEXT_PAGE + POSTFIX_COMMENTS)
async def next_comments_page(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await delete_comments_paginator_service.show_next_page(
        callback, state, session, **(await state.get_data()), parse_mode="MARKDOWN"
    )


@router.callback_query(F.data == PREV_PAGE + POSTFIX_COMMENTS)
async def prev_comments_page(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await delete_comments_paginator_service.show_prev_page(
        callback, state, session, **(await state.get_data()), parse_mode="MARKDOWN"
    )


@router.callback_query(F.data == INDICATOR_CLICKED + POSTFIX_COMMENTS)
async def indicator_clicked_comments(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await delete_comments_paginator_service.indicator_clicked(
        callback, state, session, **(await state.get_data()), parse_mode="MARKDOWN"
    )


@router.message(Command("delete"), UserManipulationFSM.delete_comments_paginator_state)
async def delete_comment(message: Message, state: FSMContext, session: AsyncSession):
    id, username = message.text[len("/delete ") :].split()
    id = int(id)
    await message.delete()
    try:
        await db.remove_review(session, username, id)
    except:
        await message.answer(
            "Не получилось удалить комментарий, вероятно, другой админ уже удалил его - перезагрузите страницу, нажав на номер страницы"
        )
        return

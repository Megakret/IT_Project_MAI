from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.ui_components.TagSelector import TagSelector
from tg_bot.routers.role_model_fsm.admin_fsm import (
    AdminPlaceRequestsFSM,
    AdminFSM,
)
from tg_bot.keyboards import admin_kb, INSERT_PLACE_TAGS_TAG
import tg_bot.routers.manager_ui.manager_requests_function as funcs

router = Router()
tag_selector = TagSelector(
    selecting_state=AdminPlaceRequestsFSM.edit_tags_input,
    router=router,
    write_messages=False,
)


@router.message(F.text == "Запросы на добавление мест", AdminFSM.start_state)
async def handle_start(message: Message, state: FSMContext):
    await funcs.show_confirmation_menu(
        message, state, AdminPlaceRequestsFSM.confirmation
    )


@router.callback_query(F.data == "yes", AdminPlaceRequestsFSM.confirmation)
async def handle_accept(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await funcs.handle_yes_command(
        callback,
        state,
        session,
        AdminPlaceRequestsFSM.looking_at_request,
        AdminFSM.start_state,
        admin_kb,
    )


@router.callback_query(F.data == "no", AdminPlaceRequestsFSM.confirmation)
async def handle_dismiss(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await funcs.handle_no_command(
        callback, state, session, AdminFSM.start_state, admin_kb
    )


@router.callback_query(F.data == "accept", AdminPlaceRequestsFSM.looking_at_request)
async def handle_accept_request(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await funcs.handle_accept(
        callback, state, session, AdminPlaceRequestsFSM.confirmation_of_acception
    )


@router.callback_query(F.data == "dismiss", AdminPlaceRequestsFSM.looking_at_request)
async def handle_dismiss_request(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await funcs.handle_dismiss(
        callback, state, session, AdminPlaceRequestsFSM.confirmation_of_dismiss
    )


@router.callback_query(F.data == "yes", AdminPlaceRequestsFSM.confirmation_of_acception)
async def handle_yes_of_confirmation_of_acceptance(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await funcs.handle_accept_confirmation_yes(
        callback,
        state,
        session,
        AdminPlaceRequestsFSM.looking_at_request,
        AdminFSM.start_state,
        admin_kb,
    )


@router.callback_query(F.data == "no", AdminPlaceRequestsFSM.confirmation_of_acception)
async def handle_no_of_confirmation_of_acceptance(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await funcs.handle_accept_confirmation_no(
        callback, state, session, AdminPlaceRequestsFSM.looking_at_request
    )


@router.callback_query(F.data == "yes", AdminPlaceRequestsFSM.confirmation_of_dismiss)
async def handle_yes_of_confirmation_of_dismiss(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await funcs.handle_dismiss_confirmation_yes(
        callback,
        state,
        session,
        AdminPlaceRequestsFSM.looking_at_request,
        AdminFSM.start_state,
        admin_kb,
    )


@router.callback_query(F.data == "no", AdminPlaceRequestsFSM.confirmation_of_dismiss)
async def handle_no_of_confirmation_of_dissmiss(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await funcs.handle_dismiss_confirmation_no(
        callback,
        state,
        session,
        AdminPlaceRequestsFSM.looking_at_request,
        AdminFSM.start_state,
        admin_kb,
    )


@router.callback_query(F.data == "edit_desc", AdminPlaceRequestsFSM.looking_at_request)
async def handle_edit(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await funcs.handle_edit(callback, state, session, AdminPlaceRequestsFSM.edit_start)


@router.callback_query(F.data == "yes", AdminPlaceRequestsFSM.edit_start)
async def handle_yes_edit(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await funcs.handle_yes_edit(
        callback, state, session, AdminPlaceRequestsFSM.waiting_for_edited_description
    )


@router.callback_query(F.data == "no", AdminPlaceRequestsFSM.edit_start)
async def handle_no_edit(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await funcs.handle_no_edit(
        callback, state, session, AdminPlaceRequestsFSM.looking_at_request
    )


@router.message(AdminPlaceRequestsFSM.waiting_for_edited_description)
async def handle_waiting_for_description(
    message: Message, state: FSMContext, session: AsyncSession
):
    await funcs.handle_new_description(
        message, state, session, AdminPlaceRequestsFSM.confirmation_of_description
    )


@router.callback_query(
    F.data == "yes", AdminPlaceRequestsFSM.confirmation_of_description
)
async def handle_yes_desc(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await funcs.handle_confirm_new_description(
        callback, state, session, AdminPlaceRequestsFSM.looking_at_request
    )


@router.callback_query(
    F.data == "no", AdminPlaceRequestsFSM.confirmation_of_description
)
async def handle_no_desc(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await funcs.handle_dismiss_new_description(
        callback, state, session, AdminPlaceRequestsFSM.edit_start
    )


@router.callback_query(F.data == "edit_tags")
async def edit_tags_start(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await funcs.handle_edit_tags_start(
        callback, state, session, AdminPlaceRequestsFSM.edit_tags_input, tag_selector
    )


@router.callback_query(
    AdminPlaceRequestsFSM.edit_tags_input, F.data == INSERT_PLACE_TAGS_TAG
)
async def tags_selected(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await funcs.handle_tags_complete_button(
        callback, state, session, AdminPlaceRequestsFSM.looking_at_request
    )


@router.callback_query(F.data == "exit", AdminPlaceRequestsFSM.looking_at_request)
async def exit(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await funcs.handle_exit(callback, state, session, AdminFSM.start_state, admin_kb)

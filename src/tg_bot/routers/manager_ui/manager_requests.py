from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.routers.role_model_fsm.manager_fsm import (
    ManagerPlaceRequestsFSM,
    ManagerFSM,
)
from tg_bot.keyboards import manager_kb
import tg_bot.routers.manager_ui.manager_requests_function as funcs

router = Router()


@router.message("Запросы на добавление мест", ManagerPlaceRequestsFSM.channel_state)
async def handle_start(message: Message, state: FSMContext):
    await funcs.show_confirmation_menu(
        message, state, ManagerPlaceRequestsFSM.confirmation
    )


@router.callback_query(F.data == "yes", ManagerPlaceRequestsFSM.confirmation)
async def handle_accept(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await funcs.handle_yes_command(
        callback, state, session, ManagerPlaceRequestsFSM.looking_at_request
    )


@router.callback_query(F.data == "no", ManagerPlaceRequestsFSM.confirmation)
async def handle_dismiss(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await funcs.handle_no_command(
        callback, state, session, ManagerFSM.start_state, manager_kb
    )


@router.callback_query(F.data == "accept", ManagerPlaceRequestsFSM.looking_at_request)
async def handle_accept_request(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await funcs.handle_accept(
        callback, state, session, ManagerPlaceRequestsFSM.confirmation_of_acception
    )


@router.callback_query(F.data == "dismiss", ManagerPlaceRequestsFSM.looking_at_request)
async def handle_dismiss_request(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession
):
    await funcs.handle_dismiss(
        callback, state, session, ManagerPlaceRequestsFSM.confirmation_of_dismiss
    )

@router.callback_query(F.data == "yes", ManagerPlaceRequestsFSM.confirmation_of_acception)
async def handle_yes_of_confirmation_of_acceptance(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await funcs.handle_accept_confirmation_yes(callback, state, session, ManagerPlaceRequestsFSM.looking_at_request)

@router.callback_query(F.data == "no", ManagerPlaceRequestsFSM.confirmation_of_acception)
async def handle_no_of_confirmation_of_acceptance(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await funcs.handle_accept_confirmation_no(callback, state, session, ManagerPlaceRequestsFSM.looking_at_request)

@router.callback_query(F.data == "yes", ManagerPlaceRequestsFSM.confirmation_of_acception)
async def handle_yes_of_confirmation_of_dismiss(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await funcs.handle_dismiss_confirmation_yes(callback, state, session, ManagerPlaceRequestsFSM.looking_at_request)

@router.callback_query(F.data == "no", ManagerPlaceRequestsFSM.confirmation_of_acception)
async def handle_no_of_confirmation_of_dissmiss(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await funcs.handle_dismiss_confirmation_no(callback, state, session, ManagerPlaceRequestsFSM.looking_at_request)

@router.callback_query(F.data == "edit", ManagerPlaceRequestsFSM.looking_at_request)
async def hande_edit(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await funcs.handle_edit(callback, state, session, ManagerPlaceRequestsFSM.waiting_for_edited_description)

@router.message(ManagerPlaceRequestsFSM.waiting_for_edited_description)
async def handle_waiting_for_description(message: Message, )
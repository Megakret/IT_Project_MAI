from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import NoResultFound
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
import tg_bot.routers.manager_ui.place_handlers.delete_place_functions as delete_place_funcs
from tg_bot.routers.role_model_fsm.manager_fsm import ManagerDeletePlaceFSM

router = Router()


@router.message(F.text == "Удалить место", ManagerDeletePlaceFSM.place_state)
async def start_handler(message: Message, state: FSMContext):
    await delete_place_funcs.start_delete_place_function(message)
    await state.set_state(ManagerDeletePlaceFSM.enter_place_id)


@router.message(ManagerDeletePlaceFSM.enter_place_id, F.text)
async def delete_place_handler(message: Message, state: FSMContext, session: AsyncSession):
    try:
        print("FUCK!!!\n\n")
        await delete_place_funcs.delete_place_function(message, session)
        await state.set_state(ManagerDeletePlaceFSM.place_state)
    except delete_place_funcs.CantDeletePlace:
        pass

from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram import Router
import logging
from tg_bot.loggers.user_logger import user_log_handler

from database.db_exceptions import UniqueConstraintError, ConstraintError
import database.db_functions as db

from tg_bot.routers.user_ui.user_fsm import UserFSM
from tg_bot.tg_exceptions import UserNotFound
from tg_bot.keyboards import get_user_keyboard


router = Router()
logger = logging.getLogger(__name__)
logger.addHandler(user_log_handler)


@router.message(CommandStart())
async def handle_cmd_start(
    message: Message, state: FSMContext, session: AsyncSession
) -> None:
    if await db.is_user_banned(session, message.from_user.id):
        await message.answer("Вы забанены!")
        return
    try:
        try:
            await db.add_user(session, message.from_user.id, message.from_user.username)
        except UniqueConstraintError as e:
            pass
        except ConstraintError as e:
            pass
        keyboard = await get_user_keyboard(session, message.from_user.id)
        await message.answer(
            (
                "Привет. Этот бот поможет тебе найти хорошее место для досуга. Выбери команду "
                "с помощью клавиатуры, или напиши, что ты хочешь от бота, и он сам активирует нужную команду."
                "Если что-то пошло не так, можешь прописать /exit, чтобы выйти из меню команды, или /start, чтобы перезагрузить бота"
            ),
            reply_markup=keyboard,
            parse_mode="MARKDOWN",
        )
    except UserNotFound as e:
        await message.answer(
            "Произошла ошибка, вашего аккаунта нет в базе. Попробуйте прописать /start еще раз."
        )
    await state.clear()
    await state.set_state(UserFSM.start_state)

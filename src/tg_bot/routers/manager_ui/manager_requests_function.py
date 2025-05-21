from aiogram.types import Message, CallbackQuery, ReplyKeyboardMarkup
from aiogram.fsm.state import State
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession

from tg_bot.keyboards import yes_no_inline


async def show_confirmation_menu(
    message: Message, state: FSMContext, next_state: State
) -> None:
    await message.answer(
        "Вы уверены, что хотите перейти в режим обработки запросов пользователей?",
        reply_markup=yes_no_inline,
    )


async def handle_yes_command(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, next_state: State
) -> None: ...


async def handle_no_command(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    next_state: State,
    keyboard: ReplyKeyboardMarkup,
) -> None: ...


async def handle_accept(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, next_state: State
) -> None:
    pass


async def handle_dismiss(
    callback: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    next_state: State,
) -> None:
    pass


async def handle_accept_confirmation_yes(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, next_state: State
): ...


async def handle_accept_confirmation_no(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, next_state: State
): ...


async def handle_dismiss_confirmation_yes(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, next_state: State
): ...


async def handle_dismiss_confirmation_no(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, next_state: State
): ...


# Выводит описание с копированием и ждёт до отправления ему исправленного сообщения
async def handle_edit(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, next_state: State
):
    pass


# Выводит сообщение с да/нет на подтверждение нового описания и сохранением места.
# При нажатии нет - в handle_edit
async def handle_new_description(
    message: Message, state: FSMContext, session: AsyncSession, next_state: State
): ...


async def handle_confirm_new_description(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, next_state: State
): ...


async def handle_dismiss_new_description(
    callback: CallbackQuery, state: FSMContext, session: AsyncSession, next_state: State
): ...


async def handle_exit(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    next_state: State,
    new_kb: ReplyKeyboardMarkup,
): ...

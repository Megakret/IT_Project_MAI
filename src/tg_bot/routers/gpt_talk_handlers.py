from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, ReplyKeyboardRemove
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from api.gpt.GptTalker import GptTalker
from tg_bot.aiogram_coros import custom_clear
from tg_bot.tg_exceptions import NoTextMessageException
from tg_bot.routers.add_place_handler import handle_cmd_start
from httpx import ReadTimeout
from sqlalchemy.ext.asyncio import AsyncSession

router = Router()


class GptTalkFSM(StatesGroup):
    talk_state = State()


@router.message(Command("talk"))
async def start_gpt(message: Message, state: FSMContext):
    gpt_talker: GptTalker = GptTalker()
    await custom_clear(state)
    await state.set_state(GptTalkFSM.talk_state)
    await state.update_data(gpt_talker=gpt_talker)
    await message.answer(
        "Хорошо, давай поговорим. Чтобы прекратить диалог введите команду /exit",
        reply_markup=ReplyKeyboardRemove(),
    )


@router.message(GptTalkFSM.talk_state, Command("exit"))
async def exit_gpt_mode(message: Message, state: FSMContext, session: AsyncSession):
    await custom_clear(state)
    await message.answer("Вы вышли из режима gpt")
    await handle_cmd_start(message, state, session)


@router.message(GptTalkFSM.talk_state)
async def send_message_to_gpt(message: Message, state: FSMContext):
    data = await state.get_data()
    try:
        gpt_talker: GptTalker = data["gpt_talker"]
        message_text: str = message.text
        if len(message_text) == 0:
            raise NoTextMessageException()
        gpt_responce: str = await gpt_talker.talk_NAC(message_text)
        await message.answer(gpt_responce)
    except KeyError as e:
        print(e)
        await message.answer(
            "Ошибка: отсутствие контекста гпт. Попробуйте снова начать диалог через /talk"
        )
    except NoTextMessageException:
        await message.answer("Вы должны отправить именно текст")
    except ReadTimeout as e:
        print(e)
        await message.answer("Не можем подклчиться к нейросети, попробуйте позже")

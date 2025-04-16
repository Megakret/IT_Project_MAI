from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.fsm.state import State, StatesGroup
from tg_bot.tg_exceptions import NoTextMessageException
from tg_bot.ui_components.GeosuggestSelector import GeosuggestSelector, SelectorStates, KEYBOARD_PREFIX, PLACE_KEY
from api.geosuggest.geosuggest import Geosuggest, GeosuggestResult
from api.geosuggest.place import Place
from database.db_functions import get_place_with_score
from database.db_functions import Place as db_Place
router = Router()


class GetPlaceStates(StatesGroup):
    enter_place = State()


geosuggest_selector = GeosuggestSelector()


class NoPlaceInDbException(Exception):
    pass

@router.message(Command("get_place"))
async def get_place_handler(message: Message, state: FSMContext):
    await state.clear()
    await message.answer("Введите название места")
    await state.set_state(GetPlaceStates.enter_place)


@router.message(GetPlaceStates.enter_place)
async def enter_place_handler(message: Message, state: FSMContext):
    await geosuggest_selector.show_suggestions(message, state)


@router.callback_query(F.data.contains(KEYBOARD_PREFIX), SelectorStates.choose_suggestion)
async def find_place_handler(callback: CallbackQuery, state: FSMContext, session: AsyncSession):
    await geosuggest_selector.selected_place(callback, state)
    data = await state.get_data()
    place: Place = data.get(PLACE_KEY)
    try:
        db_res = await get_place_with_score(session, place.get_info())
        if(db_res is None):
            raise NoPlaceInDbException()
        db_place: db_Place = db_res[0]
        score: int = db_res[1]
        if(score is None):
            await callback.message.answer(f"{db_place.name}\n{db_place.address}\n{db_place.desc}\nВы пока не оценили это место")
        else:
            await callback.message.answer(f"{db_place.name}\n{db_place.address}\n{db_place.desc}\nВаша оценка месту: {score}")
    except NoPlaceInDbException:
        await callback.message.answer("Этого места еще нет в базе, но вы можете его добавить с помощью команды /add_place")
    await state.clear()
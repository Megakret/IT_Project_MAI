from aiogram.fsm.state import State, StatesGroup


class UserFSM(StatesGroup):
    start_state = State()

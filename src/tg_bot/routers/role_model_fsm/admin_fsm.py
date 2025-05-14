from aiogram.fsm.state import StatesGroup, State


class AdminFSM(StatesGroup):
    start_state = State()
    channel_state = State()
    place_state = State()
    user_manipulation_state = State()


class AdminChannel(StatesGroup):
    add_channel_state = State()
    remove_channel_state = State()

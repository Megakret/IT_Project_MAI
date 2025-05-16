from aiogram.fsm.state import StatesGroup, State


class ManagerFSM(StatesGroup):
    start_state = State()
    channel_state = State()
    place_state = State()


class ChannelFSM(StatesGroup):
    add_channel_state = State()
    remove_channel_state = State()


class ManagerAddPlaceFSM(ManagerFSM):
    enter_place = State()
    choose_place = State()
    enter_description = State()
    enter_score = State()
    enter_comment = State()
    selecting_tags = State()

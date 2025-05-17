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
    selecting_tags = State()


class ManagerGetPlaceFSM(ManagerFSM):
    enter_place = State()
    choose_place = State()


class ManagerDeletePlaceFSM(ManagerFSM):
    enter_place_name = State()
    select_place = State()

class ManagerUpdatePlaceFSM(ManagerFSM):
    enter_place_id = State()
    enter_new_name = State()
    enter_new_description = State()
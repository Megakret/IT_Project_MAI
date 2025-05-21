from aiogram.fsm.state import StatesGroup, State


class ManagerFSM(StatesGroup):
    start_state = State()
    channel_state = State()
    place_state = State()


class ManagerChannelFSM(StatesGroup):
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
    enter_place_name = State()
    select_place = State()
    enter_new_description = State()


class ManagerPlaceRequestsFSM(ManagerFSM):
    confirmation = State()
    looking_at_request = State()
    confirmation_of_acception = State()
    confirmation_of_dismiss = State()
    edit_start = State()
    waiting_for_edited_description = State()
    confirmation_of_description = State()

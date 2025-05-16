from aiogram.fsm.state import StatesGroup, State


class AdminFSM(StatesGroup):
    start_state = State()
    channel_state = State()
    place_state = State()
    user_manipulation_state = State()


class ChannelFSM(StatesGroup):
    add_channel_state = State()
    remove_channel_state = State()


class UserManipulationFSM(StatesGroup):
    change_role_state = State()
    ban_state = State()
    ban_verify_state = State()
    ban_deletion_state = State()
    deletion_state = State()
    view_comments_state = State()

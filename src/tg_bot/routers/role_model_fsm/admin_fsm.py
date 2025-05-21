from aiogram.fsm.state import StatesGroup, State


class AdminFSM(StatesGroup):
    start_state = State()
    channel_state = State()
    place_state = State()
    user_manipulation_state = State()


class AdminChannelFSM(StatesGroup):
    add_channel_state = State()
    remove_channel_state = State()


class UserManipulationFSM(StatesGroup):
    choose_role_for_paginator_state = State()
    ban_state = State()
    ban_verify_state = State()
    ban_deletion_state = State()
    deletion_state = State()
    view_comments_state = State()
    unban_name_input_state = State()
    change_role_state = State()
    select_role_state = State()
    delete_comments_name_input = State()
    delete_comments_place_input = State()
    select_place_for_comment_deletion = State()
    delete_comments_paginator_state = State()
    choose_mode_for_deletion = State()


class AdminAddPlaceFSM(AdminFSM):
    enter_place = State()
    choose_place = State()
    enter_description = State()
    selecting_tags = State()


class AdminGetPlaceFSM(AdminFSM):
    enter_place = State()
    choose_place = State()


class AdminDeletePlaceFSM(AdminFSM):
    enter_place_name = State()
    select_place = State()


class AdminUpdatePlaceFSM(AdminFSM):
    enter_place_name = State()
    select_place = State()
    enter_new_description = State()


class AdminPlaceRequestsFSM(AdminFSM):
    confirmation = State()
    looking_at_request = State()
    confirmation_of_acception = State()
    confirmation_of_dismiss = State()
    edit_start = State()
    waiting_for_edited_description = State()
    confirmation_of_description = State()

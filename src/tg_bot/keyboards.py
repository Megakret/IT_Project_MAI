from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from tg_bot.tg_exceptions import UserNotFound
from database.db_functions import get_user_rights
from sqlalchemy.exc import NoResultFound
from sqlalchemy.ext.asyncio import AsyncSession
from tg_bot.tg_exceptions import UserNotFound
from database.db_functions import get_user_rights

SUGGEST_AMOUNT: int = 5
NEXT_PAGE = "next_page_"
PREV_PAGE = "prev_page_"
INDICATOR_CLICKED = "page_indicator_"
GET_COMMENTS_TAG = "get_comments"
SUMMARIZE_COMMENTS_TAG = "summarize_comments"
LEAVE_COMMENT_TAG = "leave_comment"
SHOW_PLACES_BY_TAG = "search_places_by_tag"
INSERT_PLACE_TAGS_TAG = "insert_place_tag"
SUMMARIZE_DESCRIPTION_TAG = "summarize_description"
suggest_place_kbs: list[InlineKeyboardMarkup] = []
for i in range(SUGGEST_AMOUNT):
    suggest_place_kbs.append(
        InlineKeyboardMarkup(
            inline_keyboard=[
                [
                    InlineKeyboardButton(
                        text="Это место", callback_data=f"suggest_place{i}"
                    )
                ]
            ]
        )
    )
starter_buttons = [
    [
        KeyboardButton(text="Добавить место"),
        KeyboardButton(text="Список мест"),
        KeyboardButton(text="Список посещённых мест"),
    ],
    [KeyboardButton(text="Найти место по тегу"), KeyboardButton(text="Найти место")],
]

starter_kb = ReplyKeyboardMarkup(keyboard=starter_buttons)

starter_manager_kb = ReplyKeyboardMarkup(
    keyboard=starter_buttons + [[KeyboardButton(text="Панель менеджера")]],
)

starter_admin_kb = ReplyKeyboardMarkup(
    keyboard=starter_buttons + [[KeyboardButton(text="Админ панель")]],
)

show_comments_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Пересказ описания", callback_data=SUMMARIZE_DESCRIPTION_TAG
            )
        ],
        [
            InlineKeyboardButton(
                text="Показать комментарии", callback_data=GET_COMMENTS_TAG
            )
        ],
        [
            InlineKeyboardButton(
                text="Суммаризовать комментарии", callback_data=SUMMARIZE_COMMENTS_TAG
            )
        ],
        [InlineKeyboardButton(text="Оставить отзыв", callback_data=LEAVE_COMMENT_TAG)],
    ]
)
show_places_by_tag_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Найти места по тегу", callback_data=SHOW_PLACES_BY_TAG
            )
        ]
    ]
)
insert_place_tags_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(
                text="Добавить теги к месту", callback_data=INSERT_PLACE_TAGS_TAG
            )
        ]
    ]
)

manager_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Управление ТГ каналами"),
            KeyboardButton(text="Управление местами"),
            KeyboardButton(text="Запросы на добавление мест"),
        ],
        [KeyboardButton(text="Назад")],
    ],
)


admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Управление ТГ каналами"),
            KeyboardButton(text="Управление местами"),
        ],
        [
            KeyboardButton(text="Запросы на добавление мест"),
            KeyboardButton(text="Управление пользователями"),
        ],
        [KeyboardButton(text="Назад")],
    ],
)

channel_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить ТГ канал"),
            KeyboardButton(text="Подключённые каналы"),
            KeyboardButton(text="Удалить канал"),
        ],
        [KeyboardButton(text="Помощь"), KeyboardButton(text="Назад")],
    ],
)

place_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить место"),
            KeyboardButton(text="Список мест"),
            KeyboardButton(text="Найти место"),
        ],
        [KeyboardButton(text="Помощь"), KeyboardButton(text="Назад")],
    ],
)
yes_no_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Да"),
            KeyboardButton(text="Нет"),
        ]
    ],
    resize_keyboard=True,
)
place_manager_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить место"),
            KeyboardButton(text="Редактировать место"),
            KeyboardButton(text="Удалить место"),
        ],
        [KeyboardButton(text="Найти место"), KeyboardButton(text="Назад")],
    ],
)

request_manager_kb = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Принять", callback_data="accept"),
            InlineKeyboardButton(text="Отклонить", callback_data="dismiss"),
        ],
        [
            InlineKeyboardButton(
                text="Редактировать описание", callback_data="edit_desc"
            ),
            InlineKeyboardButton(text="Редактировать теги", callback_data="edit_tags"),
        ],
        [InlineKeyboardButton(text="Назад", callback_data="exit")],
    ]
)

select_comment_deletion_mode_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Поиск по месту")],
        [KeyboardButton(text="Поиск по пользователю")],
    ]
)

user_manipulation_admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Список пользователей"),
            KeyboardButton(text="Забанить пользователя"),
            KeyboardButton(text="Разбанить пользователя"),
        ],
        [
            KeyboardButton(text="Удаление комментариев"),
            KeyboardButton(text="Изменить роль пользователя"),
        ],
        [
            KeyboardButton(text="Назад"),
        ],
    ]
)

yes_no_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [
            InlineKeyboardButton(text="Да", callback_data="yes"),
            InlineKeyboardButton(text="Нет", callback_data="no"),
        ]
    ]
)

set_role_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Пользователь", callback_data="user")],
        [InlineKeyboardButton(text="Менеджер", callback_data="manager")],
    ]
)

set_role_owner_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Пользователь", callback_data="user")],
        [InlineKeyboardButton(text="Менеджер", callback_data="manager")],
        [InlineKeyboardButton(text="Админ", callback_data="admin")],
    ]
)

chose_role_for_paginator_inline = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="Пользователь", callback_data="user")],
        [InlineKeyboardButton(text="Менеджер", callback_data="manager")],
        [InlineKeyboardButton(text="Админ", callback_data="admin")],
        [InlineKeyboardButton(text="Заблокированные", callback_data="banned")],
    ]
)

back_kb = ReplyKeyboardMarkup(
    keyboard=[[KeyboardButton(text="Назад")]], resize_keyboard=True
)


def generate_page_kb(page: int, postfix: str) -> InlineKeyboardMarkup:
    page_select_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="<-", callback_data=PREV_PAGE + postfix),
                InlineKeyboardButton(
                    text=f"{page}", callback_data=INDICATOR_CLICKED + postfix
                ),
                InlineKeyboardButton(text="->", callback_data=NEXT_PAGE + postfix),
            ]
        ]
    )
    return page_select_kb


async def get_user_keyboard(session: AsyncSession, id: int) -> ReplyKeyboardMarkup:
    try:
        right: int = await get_user_rights(session, id)
        print(right)
        match right:
            case 4:
                return starter_admin_kb
            case 3:
                return starter_admin_kb
            case 2:
                return starter_manager_kb
            case 1:
                return starter_kb
    except NoResultFound as e:
        raise UserNotFound("While getting user's rights he was not found.")

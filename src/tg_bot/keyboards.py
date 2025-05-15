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

SUGGEST_AMOUNT: int = 5
NEXT_PAGE = "next_page_"
PREV_PAGE = "prev_page_"
INDICATOR_CLICKED = "page_indicator_"
GET_COMMENTS_TAG = "get_comments"
SUMMARIZE_COMMENTS_TAG = "summarize_comments"
LEAVE_COMMENT_TAG = "leave_comment"
SHOW_PLACES_BY_TAG = "search_places_by_tag"
INSERT_PLACE_TAGS_TAG = "insert_place_tag"
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
    resize_keyboard=True,
)

starter_admin_kb = ReplyKeyboardMarkup(
    keyboard=starter_buttons + [[KeyboardButton(text="Админ панель")]],
)

show_comments_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
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
        [
            InlineKeyboardButton(
                text="Оставить комментарий", callback_data=LEAVE_COMMENT_TAG
            )
        ],
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
            KeyboardButton(text="Запросы на добавления"),
        ],
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True,
)


admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Управление ТГ каналами"),
            KeyboardButton(text="Управление местами"),
        ],
        [
            KeyboardButton(text="Запросы на добавления"),
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
    resize_keyboard=True,
)

place_kb = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text="Добавить место"),
            KeyboardButton(text="Список мест"),
            KeyboardButton(text="Найти место"),
        ],
        [KeyboardButton(text="Помощь"), KeyboardButton(text="Назад")],
    ]
)

place_manager_kb = ReplyKeyboardMarkup(keyboard=[])


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
        match right:
            case 3:
                return starter_admin_kb
            case 2:
                return starter_manager_kb
            case 1:
                return starter_kb
    except NoResultFound as e:
        print(e.message)
        raise UserNotFound("While getting user's rights he was not found.")

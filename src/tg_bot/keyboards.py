from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

SUGGEST_AMOUNT: int = 5
NEXT_PAGE = "next_page_"
PREV_PAGE = "prev_page_"
INDICATOR_CLICKED = "page_indicator_"
GET_COMMENTS_TAG = "get_comments"
SUMMARIZE_COMMENTS_TAG = "summarize_comments"
LEAVE_COMMENT_TAG = "leave_comment"
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
starter_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/add_place")],
        [KeyboardButton(text="/place_list")],
        [KeyboardButton(text="/user_place_list")],
        [KeyboardButton(text="/get_place")],
    ],
    resize_keyboard=True,
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
        ]
    ]
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

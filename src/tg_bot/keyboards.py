from aiogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton,
)
from aiogram.utils.keyboard import InlineKeyboardBuilder

SUGGEST_AMOUNT: int = 5
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
    ],
    resize_keyboard=True,
)


def generate_page_kb(page: int, postfix: str) -> InlineKeyboardMarkup:
    page_select_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="<-", callback_data=f"prev_page_{postfix}"),
                InlineKeyboardButton(
                    text=f"{page}", callback_data=f"page_indicator_{postfix}"
                ),
                InlineKeyboardButton(text="->", callback_data=f"next_page_{postfix}"),
            ]
        ]
    )
    return page_select_kb

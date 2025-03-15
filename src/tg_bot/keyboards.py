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


def generate_page_kb(page: int, max_page: int) -> InlineKeyboardMarkup:
    page_select_kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="<-", callback_data="prev_page"),
                InlineKeyboardButton(
                    text=f"{page+1}/{max_page}", callback_data="page_indicator"
                ),
                InlineKeyboardButton(text="->", callback_data="next_page"),
            ]
        ]
    )
    return page_select_kb

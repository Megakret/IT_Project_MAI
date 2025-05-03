from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from tg_bot.keyboards import generate_page_kb
import tg_bot.aiogram_coros as utils
from typing import Callable, Awaitable
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup


class NoMorePages(Exception):
    def __init__(self, page: int):
        super().__init__(f"No pages past {page}")
        self._page = page


class PaginatorService:
    pass


class Paginator:
    def __init__(
        self,
        items_per_page: int,
        get_data_by_page: Callable[[int, int], Awaitable[list[str]]],
        paginator_service: PaginatorService,
    ):
        self._get_data_by_page = get_data_by_page
        self._current_page = 1
        self._items_per_page = items_per_page
        self._message: Message = None
        self._paginator_service = paginator_service

    @property
    def message(self):
        return self._message

    async def _update(self, page: int, *args, **kwargs):
        items: list[str] = await self._get_data_by_page(
            page, self._items_per_page, *args, **kwargs
        )
        text: str = "\n-----------\n".join(items)
        if text == "":
            raise NoMorePages(page)
        await self._message.edit_text(text)
        await self._message.edit_reply_markup(
            reply_markup=self._paginator_service.update_kb(page)
        )

    async def setup(self, message: Message, *args, **kwargs):
        self._current_page = 1
        try:
            self._message = await message.answer("Загрузка...")
            await self._update(self._current_page, *args, **kwargs)
        except NoMorePages as e:
            await self._message.edit_text(self._paginator_service.no_pages_message)

    async def show_next_page(self, callback: CallbackQuery, *args, **kwargs):
        try:
            await self._update(self._current_page + 1, *args, **kwargs)
            self._current_page += 1
        except NoMorePages:
            await callback.answer("Вы на последней странице")

    async def show_prev_page(self, callback: CallbackQuery, *args, **kwargs):
        try:
            if self._current_page - 1 <= 0:
                raise NoMorePages(self._current_page - 1)
            await self._update(self._current_page - 1, *args, **kwargs)
            self._current_page -= 1
        except NoMorePages:
            await callback.answer("Вы на первой странице")

    async def indicator_clicked(self, callback: CallbackQuery):
        await callback.answer(f"Вы на странице {self._current_page}")

    async def reattach(self, message: Message, *args, **kwargs):
        self._message = message
        await self._update(self._current_page, *args, **kwargs)


class PaginatorService:
    def update_kb(self, page: int) -> InlineKeyboardMarkup:
        return generate_page_kb(page, self._postfix)

    async def start_paginator(
        self, message: Message, state: FSMContext, *args, **kwargs
    ) -> (
        None
    ):  # paginator service automatically creates message with paginator and generates the first page with given parameters
        paginator = Paginator(self._items_per_page, self._get_data_by_page, self)
        await paginator.setup(message, *args, **kwargs)
        await state.update_data({("paginator" + self._postfix): paginator})

    async def _prepare_paginator(
        self, callback: CallbackQuery, state: FSMContext, *args, **kwargs
    ) -> Paginator:
        data: dict = await state.get_data()
        try:
            paginator: Paginator = data["paginator" + self._postfix]
        except KeyError:
            paginator = Paginator(self._items_per_page, self._get_data_by_page, self)
            await state.update_data({("paginator" + self._postfix): paginator})
        if (
            paginator.message is None
        ) or callback.message.message_id != paginator.message.message_id:
            await paginator.reattach(callback.message, *args, **kwargs)
        return paginator

    async def indicator_clicked(
        self, callback: CallbackQuery, state: FSMContext, *args, **kwargs
    ) -> None:
        paginator: Paginator = await self._prepare_paginator(
            callback, state, *args, **kwargs
        )
        await paginator.indicator_clicked(callback)

    async def show_next_page(
        self, callback: CallbackQuery, state: FSMContext, *args, **kwargs
    ) -> None:
        paginator: Paginator = await self._prepare_paginator(
            callback, state, *args, **kwargs
        )
        await paginator.show_next_page(callback, *args, **kwargs)

    async def show_prev_page(
        self, callback: CallbackQuery, state: FSMContext, *args, **kwargs
    ) -> None:
        paginator: Paginator = await self._prepare_paginator(
            callback, state, *args, **kwargs
        )
        await paginator.show_prev_page(callback, *args, **kwargs)

    @property
    def no_pages_message(self):
        return self._no_pages_message

    def __init__(  # declare it as a global variable
        self,
        postfix: str,
        items_per_page: int,
        get_data_by_page: Callable[[int, int], Awaitable[list[str]]],
        no_pages_message: str,
    ):
        self._postfix = postfix
        self._items_per_page = items_per_page
        self._get_data_by_page = get_data_by_page
        self._no_pages_message = no_pages_message
        # router.message.register(self.start_paginator, Command(appear_command))
        # router.callback_query.register(
        #     self.show_next_page, F.data == f"next_page_{postfix}"
        # )
        # router.callback_query.register(
        #     self.show_prev_page, F.data == f"prev_page_{postfix}"
        # )
        # router.callback_query.register(
        #     self.indicator_clicked, F.data == f"page_indicator_{postfix}"
        # )

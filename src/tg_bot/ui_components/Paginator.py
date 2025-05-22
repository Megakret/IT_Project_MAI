from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from tg_bot.keyboards import generate_page_kb
from typing import Callable, Awaitable
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from aiogram.types import InlineKeyboardMarkup
from aiogram.exceptions import TelegramBadRequest


class NoMorePages(Exception):
    def __init__(self, page: int):
        super().__init__(f"No pages past {page}")
        self._page = page


class PaginatorService:
    pass


class NoPaginatorFound(Exception):
    pass


class Paginator:
    """Paginator instance which is anchored to telegram message. Should not be used in external code.\n
    This class exists only for paginator service.\n
    \n
    items_per_page (int): amount of data which is displayed on a single page\n
    get_data_by_page: function which accepts page (int) and items_per_page (int) as required parameters and\n
    any other parameter as you want\n
    paginator_service: PaginatorService instance that created paginator\n
    message: message that paginator is anchored to\n
    """

    def __init__(
        self,
        items_per_page: int,
        get_data_by_page: Callable[[int, int], Awaitable[list[str]]],
        paginator_service: PaginatorService,
        message: Message = None,
    ):
        self._get_data_by_page = get_data_by_page
        self._current_page = 1
        self._items_per_page = items_per_page
        self._message: Message = message
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
        if text == self.message.text:
            return
        try:
            await self._message.edit_text(
                text, reply_markup=self._paginator_service.update_kb(page), **kwargs
            )
        except TelegramBadRequest as e:
            print(f"Paginator received same message")

    async def update(self, *args, **kwargs):
        try:
            await self._update(self._current_page, *args, **kwargs)
        except NoMorePages:
            await self._message.edit_text(self._paginator_service.no_pages_message)

    async def setup(self, message: Message, *args, **kwargs):
        self._current_page = 1
        try:
            self._message = await message.answer("Загрузка...", **kwargs)
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
    """Creates paginator service which is used for displaying paged data to telegram\n
    Create it as a global variable in same file with the router. Invoke its functions yourself.\n
    Declare a function that gets paged data.\n
    Keyword arguments:\n
    postfix (str): postfix that is appended to callback data which is sent by paginator keyboard\n
    items_per_page (int): amount of data which is displayed on a single page\n
    get_data_by_page: function which accepts page (int) and items_per_page (int) as required parameters and\n
    any other parameter as you want\n
    no_pages_message (str): message that is displayed instead of paginator when no data for paging\n
    """

    def update_kb(self, page: int) -> InlineKeyboardMarkup:
        return generate_page_kb(page, self._postfix)

    async def start_paginator_on_message(
        self, message: Message, state: FSMContext, *args, **kwargs
    ) -> None:
        """starts paginator on already existing message\n

        Keyword arguments:\n
        message: message that paginator is anchored to\n
        state: fsmcontext of the user\n
        *args, **kwargs: parameters which are passed to self._get_data_by_page\n
        """

        paginator = Paginator(
            self._items_per_page, self._get_data_by_page, self, message
        )
        try:
            await paginator._update(1, *args, **kwargs)
            await state.update_data({("paginator" + self._postfix): paginator})
        except:
            await message.edit_text(self._no_pages_message)

    async def start_paginator(
        self, message: Message, state: FSMContext, *args, **kwargs
    ) -> None:
        """paginator service automatically creates message with paginator and generates the first page with given parameters\n
        Keyword arguments:\n
        message: message that is used to locate user chat. Bot will answer to it with paginator\n
        state: fsmcontext of the user\n
        *args, **kwargs: parameters which are passed to self._get_data_by_page\n
        """
        paginator = Paginator(self._items_per_page, self._get_data_by_page, self)
        await paginator.setup(message, *args, **kwargs)
        await state.update_data({("paginator" + self._postfix): paginator})

    async def _prepare_paginator(
        self, callback: CallbackQuery, state: FSMContext, *args, **kwargs
    ) -> Paginator:
        """prepares paginator before displaying page. Reattaches it to another message if it needs to\n

        Keyword arguments:\n
        callback: callback that comes from paginator button\n
        state: fsmcontext of the user\n
        *args, **kwargs: parameters which are passed to self._get_data_by_page\n
        """

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
        """Must be invoked on button which has current page number. Updates paginator if new data occured or some deleted.\n

        Keyword arguments:\n
        callback: callback that comes from paginator button\n
        state: fsmcontext of the user\n
        *args, **kwargs: parameters which are passed to self._get_data_by_page\n
        """

        paginator: Paginator = await self._prepare_paginator(
            callback, state, *args, **kwargs
        )
        await paginator.update(*args, **kwargs)
        await paginator.indicator_clicked(callback)

    async def show_next_page(
        self, callback: CallbackQuery, state: FSMContext, *args, **kwargs
    ) -> None:
        """Must be invoked on next page button press\n

        Keyword arguments:\n
        callback: callback that comes from paginator button\n
        state: fsmcontext of the user\n
        *args, **kwargs: parameters which are passed to self._get_data_by_page\n
        """

        paginator: Paginator = await self._prepare_paginator(
            callback, state, *args, **kwargs
        )
        await paginator.show_next_page(callback, *args, **kwargs)

    async def show_prev_page(
        self, callback: CallbackQuery, state: FSMContext, *args, **kwargs
    ) -> None:
        """Must be invoked on prev page button press\n

        Keyword arguments:\n
        callback: callback that comes from paginator button\n
        state: fsmcontext of the user\n
        *args, **kwargs: parameters which are passed to self._get_data_by_page\n
        """
        paginator: Paginator = await self._prepare_paginator(
            callback, state, *args, **kwargs
        )
        await paginator.show_prev_page(callback, *args, **kwargs)

    async def update_paginator(self, state: FSMContext, *args, **kwargs):
        """Use it to update current paginator by some event which are not paginator button presses\n

        Keyword arguments:\n
        state: fsmcontext of the user\n
        *args, **kwargs: parameters which are passed to self._get_data_by_page\n
        """
        data: dict = await state.get_data()
        try:
            current_paginator: Paginator = data["paginator" + self._postfix]
            await current_paginator.update(*args, **kwargs)
        except KeyError:
            raise NoPaginatorFound

    @property
    def no_pages_message(self):
        return self._no_pages_message

    def __init__(
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

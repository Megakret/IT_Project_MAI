from aiogram.types import Message
from aiogram.fsm.context import FSMContext
import asyncio
from httpx import TransportError
from typing import Coroutine

EXPECTED_TIME = 5
REQUEST_TAG = "request_tag"


class RetryPolicyRequest:
    def __init__(
        self,
        async_request: Coroutine,
        state: FSMContext,
        expected_time: int = EXPECTED_TIME,
    ):
        self._async_request = asyncio.create_task(async_request)
        self._expected_time = expected_time
        self._context = state

    async def request(self, message_to_answer: Message):
        try:
            await self._context.update_data(**{REQUEST_TAG: self})
            self._message = await message_to_answer.answer("Ожидайте...")
            result, _ = await asyncio.gather(self._async_request, self._monitor())
            await self._message.delete()
            return result
        except TransportError:
            await self._message.edit_text("Запрос не удался. Попробуйте еще раз позже.")
        finally:
            await self._context.update_data(**{REQUEST_TAG: None})

    async def _monitor(self):
        await asyncio.sleep(self._expected_time)
        if not self._async_request.done():
            await self._message.edit_text(
                "Запрос занимает больше времени, чем ожидалось..."
            )

    async def drop_request(self):
        await self._context.update_data(**{REQUEST_TAG: None})
        self._async_request.cancel()
        await self._message.delete()

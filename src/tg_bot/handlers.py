from aiogram import Router
from aiogram.filters import CommandStart, Command
from aiogram.types import Message
router = Router()

@router.message(CommandStart())
async def handle_cmd_start(message: Message) -> None:
    await message.answer("Привет. Напиши /fun")

@router.message(Command("fun"))
async def handle_cmd_fun(message: Message) -> None:
    await message.answer_animation("https://media1.tenor.com/m/LWr0XvjOuo0AAAAC/pearto-pear.gif")

from aiogram.methods.send_message import SendMessage


async def message_sender_wrap(sender: SendMessage):
    await sender

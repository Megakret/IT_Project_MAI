from aiogram import Router, types
from sqlalchemy.ext.asyncio import AsyncSession
from asyncio import gather
from api.gpt.GptTgReview import GptTgReview
from api.geosuggest.geosuggest import Geosuggest
import database.db_functions as db
from database.db_exceptions import UniqueConstraintError
from tg_bot.routers.channel_fetch_functions import (
    check_channel,
    parseAddress,
    parseName,
)


router = Router()
reviewer = GptTgReview()


@router.channel_post()
async def fetch_data(message: types.Message, session: AsyncSession) -> None:
    """
    currently in development, only prints to the console, I wait DB for tg posts
    """
    if not await check_channel(message.chat.username, session):
        return
    out: dict = await reviewer.summarize_review_NAC(
        str(message.caption) + str(message.text)
    )
    print("Names: ", out["place"])
    print("Reviews: ", out["review"])
    print(message.caption)
    print("----------------")
    print(message.text)
    if out["error"]:
        print("Message from " + message.chat.full_name + " is not about place")
        return
    print("passed if")
    geosuggest = Geosuggest()
    tasks = [geosuggest.request(place) for place in out["place"]]
    print("passed corutine creation")
    places = await gather(*tasks)
    add_tasks = [
        db.add_place(
            session, parseName(places[i]), parseAddress(places[i]), out["review"][i]
        )
        for i in range(len(places))
    ]
    try:
        await gather(*add_tasks)
    except UniqueConstraintError as e:
        print(e.message)

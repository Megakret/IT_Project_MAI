from aiogram import Router, types
from sqlalchemy.ext.asyncio import AsyncSession
from asyncio import gather
from api.gpt.GptTgReview import GptTgReview
from api.geosuggest.geosuggest import Geosuggest
import database.db_functions as db
from database.db_exceptions import UniqueConstraintError
from tg_channel_fetcher.channel_fetch_functions import (
    check_channel,
    parseAddress,
    parseName,
)
import logging
from tg_bot.loggers.channel_fetch_logger import channel_log_handler


router = Router()
reviewer = GptTgReview()
logger = logging.getLogger(__name__)
logger.addHandler(channel_log_handler)


@router.channel_post()
async def fetch_data(message: types.Message, session: AsyncSession) -> None:
    if not await check_channel(message.chat.username, session):
        return
    out: dict = await reviewer.summarize_review_NAC(
        str(message.caption) + str(message.text)
    )
    logger.debug("Names: ", out["place"])
    logger.debug("Reviews: ", out["review"])
    logger.debug(message.caption)
    logger.debug("----------------")
    logger.debug(message.text)
    if out["error"]:
        logger.debug("Message from " + message.chat.full_name + " is not about place")
        return
    geosuggest = Geosuggest()
    tasks = [geosuggest.request(place) for place in out["place"]]
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
        logger.error(e.message, exc_info=e)


@router.error()
async def handle_errors(error: types.ErrorEvent):
    logger.critical("Uncaught error appeared: %s", error.exception, exc_info=True)

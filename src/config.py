from dotenv import load_dotenv
from os import getenv
from httpx_retries import Retry, RetryTransport

load_dotenv()

MAX_COMMENT_SIZE = 400
MAX_DESCRIPTION_VIEWSIZE = 400
BOT_USERNAME = "entertainment_assistant_bot"
BOT_API_KEY = getenv("BOT_TOKEN")
GEOSUGGEST_API_KEY = getenv("GEOSUGGEST_KEY")
GPT_KEY = getenv("GPT_API_KEY")
GPT_INDETIFICATION_KEY = getenv("GPT_INDENTIFICATION")

RETRY_POLICY_TRANSPORT = RetryTransport(retry=Retry(backoff_factor=2))

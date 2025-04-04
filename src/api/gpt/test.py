import requests
from os import getenv
from dotenv import load_dotenv

load_dotenv()

ind_key = getenv("GPT_INDENTIFICATION")

prompt = {
    "modelUri": f"gpt://{ind_key}/yandexgpt-lite",
    "completionOptions": {
        "stream": False,
        "temperature": 0.6,
        "maxTokens": 2000
    },
    "messages": [
        {
            "role": "system",
            "text": "Ты - консультант, который помогает людям найти место, где можно отдохнуть. Не советуй мест для взрослых, на любые вопросы не по теме отказывайся отвечать."
        }
    ]
}

url = "https://llm.api.cloud.yandex.net/foundationModels/v1/completion"
headers = {
    "Content-Type": "application/json",
    "Authorization": f"Api-Key {getenv("GPT_API_KEY")}"
}

response = requests.post(url, headers=headers, json=prompt)
result = response.text
print(result)

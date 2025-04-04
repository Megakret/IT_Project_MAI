from dotenv import load_dotenv
from os import getenv
import json
import requests
from Gpt import Gpt


class GptTalker(Gpt):

    def __init__(self):
        super().__init__("src/api/gpt/starting_prompt.json")

    def communicate(self, message: str) -> str:
        self._append_message({"role": "user", "text": message})
        response = requests.post(GptTalker.url, headers=GptTalker.headers, json=self.prompt)
        self._append_message(response.json()["result"]["alternatives"][0]["message"])
        return self


if __name__ == "__main__":
    load_dotenv()
    gpt: GptTalker = GptTalker()
    while (s := input()) != "\n":
        print(gpt.communicate(s))
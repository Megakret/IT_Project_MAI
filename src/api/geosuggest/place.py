from typing import Tuple
from typing import Dict
import json


class Place:
    __TRANSLATIONS: Dict[str, str] = None
    with open("src/api/geosuggest/translation.json", "r", encoding="utf-8") as file:
        __TRANSLATIONS = json.load(file)

    def __init__(self, data: dict):
        self.__title: str = data["title"]["text"]
        self.__subtitle: str = data["subtitle"]["text"]
        # Translates tags to Russian
        self.__tags: Tuple[str] = tuple(
            map(
                lambda x: Place.__TRANSLATIONS[x] if x in Place.__TRANSLATIONS else x,
                data["tags"],
            )
        )
        self.__combined: str = (
            f"{self.__title}\n{self.__subtitle}\nТеги:\n{", ".join(self.__tags)}"
        )

    def get_name(self) -> str:
        return self.__title

    def get_info(self) -> str:
        return self.__subtitle

    def get_tags(self) -> Tuple[str]:
        return self.__tags

    def __str__(self) -> str:
        return self.__combined

    def __repr__(self) -> str:
        return f"Place({self.__title, self.__subtitle, self.__tags})"

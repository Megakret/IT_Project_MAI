import json
import os
from api.geosuggest.geosuggest import Geosuggest, GeosuggestResult
from api.geosuggest.place import Place

PLACES_PER_PAGE: int = 3


class PlaceSchema:
    def __init__(self, name: str, description: str, score: int, info: str):
        self.name = name
        self.description = description
        self.score = score
        self.info = info

    def __repr__(self):
        return f"<PlaceSchema: name: {self.name}, description: {self.description}, score: {self.score}>"


def create_placeholder() -> None:
    with open(os.path.dirname(__file__) + "/place_list.json", "w") as file:
        responces: list[GeosuggestResult] = [
            Geosuggest.request(place)
            for place in (
                "Кремль",
                "ВДНХ",
                "The бык",
                "Colliseum игровой клуб",
                "Метрополис",
            )
        ]
        result_dict: dict[str, dict[str, int | str]] = {}
        for responce in responces:
            for place in responce:
                result_dict[place.get_name()] = {
                    "info": place.get_info(),
                    "tags": place.get_tags(),
                    "score": 10,
                    "description": "some place",
                }
        json.dump(result_dict, file, ensure_ascii=False, indent=2)


def get_places_by_page(page: int) -> list[str]:  # 0 indexation
    with open(os.path.dirname(__file__) + "/place_list.json", "r") as file:
        raw_place_dict: dict[str, dict[str, int | str]] = json.load(file)
        place_list: list[PlaceSchema] = [
            PlaceSchema(name, props["description"], props["score"], props["info"])
            for name, props in raw_place_dict.items()
        ]
    lower_bound: int = PLACES_PER_PAGE * page
    upper_bound: int = lower_bound + PLACES_PER_PAGE
    print(lower_bound, upper_bound)
    if lower_bound >= len(place_list) or lower_bound < 0:
        raise KeyError("This page doesn't exist")
    places_info: list[str] = []
    for i in range(lower_bound, min(upper_bound, len(place_list))):
        place: PlaceSchema = place_list[i]
        places_info.append(
            "\n".join(
                [
                    f"Название: {place.name}",
                    f"Адрес: {place.info}",
                    f"Описание: {place.description}",
                    f"Оценка: {place.score}",
                ]
            )
        )
    return places_info


def get_page_count() -> int:
    with open(os.path.dirname(__file__) + "/place_list.json", "r") as file:
        raw_place_dict: dict[str, dict[str, int | str]] = json.load(file)
        return len(raw_place_dict) // PLACES_PER_PAGE

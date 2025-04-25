import os
import json


def get_comments(page: int, places_per_page: int, address: str) -> list[str]:
    all_comments: dict[str, list[str]]
    with open("src/tg_bot/test_utils/comments/comments.json") as file:
        all_comments = json.load(file)
    return all_comments.get(address)[
        (page - 1) * places_per_page : page * places_per_page
    ]


if __name__ == "__main__":
    print(get_comments(1, 4, "Салон красоты · Москва, Ленинградское шоссе, 8к3"))

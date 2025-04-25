import os
import json
from typing import Self

class CommentsMock:
    instance: Self = None
    comments: dict[str, list[str]]
    def __init__(self):
        if(CommentsMock.instance != None):
            return
        with open("src/tg_bot/test_utils/comments/comments.json") as file:
            self.comments = json.load(file)
            CommentsMock.instance = self
    def get_comments_by_page(self, page: int, places_per_page: int, address: str) -> list[str]:
        return self.comments.get(address)[
            (page - 1) * places_per_page : page * places_per_page
        ]
    def get_all_comments(self, address: str) -> list[str]:
        return self.comments.get(address)
    def add_comment(self, address: str, comment: str) -> None:
        if(address not in self.comments):
            self.comments[address] = []
        self.comments[address].append(comment)

comments_mock = CommentsMock()


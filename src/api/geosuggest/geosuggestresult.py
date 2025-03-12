from typing import List
from typing import Tuple
from typing import Dict
from place import Place


class GeosuggestResult:
    def __init__(self, result: List[Dict]):
        self.__data: Tuple[Place] = tuple(map(lambda x: Place(x), result))

    def get_places(self) -> Tuple[str]:
        return tuple(map(lambda x: x.get_name(), self.__data))

    def get_info(self) -> Tuple[str]:
        return tuple(map(lambda x: x.get_info(), self.__data))

    def get_tags(self) -> Tuple[Tuple[str]]:
        return tuple(map(lambda x: x.get_tags(), self.__data))

    def get_messages(self) -> Tuple[str]:
        return tuple(map(str, self.__data))

    def __str__(self) -> str:
        return "\n\n".join(self.get_messages())

    def repr(self) -> str:
        return f"GeosuggestResult({", ".join(map(repr, self.__data))})"

    # return ith place as Place object
    def __getitem__(self, key: int) -> Place:
        return self.__data[key]

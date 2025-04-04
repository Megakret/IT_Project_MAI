## Работа со всеми функциями API
Работа происходит асинхронно, при вызове нужно создать AsyncClient и передать его в функцию. Пример:
``` python
from GptTalker import GptTalker
from httpx import AsyncClient  

async def talk(message: str) -> str:
    talker: GptTalker = GptTalker()
    async with AsyncClient() as client:
        result: str = await talker.talk(client, message)
    return result
```
## Summary отзывов:
Данная фича реализована через вызов функции GptSummary.summary(client: httpx.AssyncClient, reviews: list[str]) -> str. Возвращает строку - summary отзывов.
Пример использования:
```python
from GptSummarize import summarize
from httpx import AsyncClient


async def summarize_example() -> str:
    reviews: list[str] = [ ... ]
    async with AsyncClient() as client:
        result = await summarize(client, reviews)
    return result
```
## Болталка
Для каждого пользователя должна создаваться отдельно и не должна удаляться. После добавления БД планируется добавить возможность получения прошлого диалога с пользователем. Является экземпляром класса GptTalker. Пример:
```python
from GptTalker import GptTalker
from httpx import AsyncClient

async def talk() -> None:
	talker: GptTalker = GptTalker()
	async with AsyncClient() as client:
		while (s := input()):
			print(await talker.talk(client, s))
```


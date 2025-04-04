from Gpt import Gpt
import asyncio

class GptSummarize(Gpt):
    def __init__(self, requests: list[str] = []):
        super().__init__("src/api/gpt/review_prompt.json")
        self.__messages = requests.copy()

    def append_review(self, review: str | list[str]) -> None:
        if (isinstance(review, str)):
            self.__messages.append(review)
            return
        self.__messages += review

    def __construct_message(self) -> str:
        s = "Сделай выжимку из данных отзывов о местах:\n\n"
        for i, l in enumerate(self.__messages):
            s += f"{i + 1}. {l}\n\n"
        return s

    async def summarize(self) -> str:
        if len(self.__messages) == 0:
            return ""
        self._append_message({"role": "user", "text": self.__construct_message()})
        r = await self._request()
        print(r.json())
        return r.json()["result"]["alternatives"][0]["message"]["text"]

    def clear_messages(self) -> None:
        self.__messages.clear()

async def main():
    from dotenv import load_dotenv
    load_dotenv()
    sum = GptSummarize(["Были вчера в La Bella Italia — всё было идеально! Паста карбонара просто таяла во рту, сервис на высоте, атмосфера уютная. Особенно понравился десерт — тирамису свежий и не приторный. Обязательно вернёмся!",
                        "Заказывал пиццу Маргариту — тонкое тесто, соус просто бомба, сыр тянется, как надо! Персонал дружелюбный, принесли всё быстро. Цены адекватные за такое качество. Рекомендую!",
                        "Ресторан La Bella Italia стал нашим любимым! Вино подобрали идеально под блюдо, официант Антон дал классные рекомендации. Интерьер стильный, музыка ненавязчивая. 10/10!",
                        "Ожидали большего. Паста \"Болоньезе\" была пересолена, мясо жёсткое. Официант забыл принести напитки, пришлось напоминать дважды. За такие деньги — неоправданно.",
                        "Заказали стейк и ризотто — ждали 40 минут, хотя ресторан был полупустой. Еда пришла еле тёплая. На претензии лишь пожали плечами. Больше не пойдём.",
                        "Морепродукты в \"Паста фрутти ди маре\" были несвежими, чувствовался неприятный привкус. Цены высокие, а качество не тянет даже на средний уровень. Жаль потраченных денег."])
    tasks = [sum.summarize(), sum.summarize()]
    print(await asyncio.gather(*tasks))
    
if __name__ == "__main__":
    asyncio.run(main())

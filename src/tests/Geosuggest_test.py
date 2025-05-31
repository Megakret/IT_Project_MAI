import pytest
from api.geosuggest.geosuggest_yandex import GeosuggestYandex


@pytest.mark.asyncio
async def test_geosuggest_normal_request():
    result = await GeosuggestYandex.request("Метрополис")
    assert len(result) > 0


@pytest.mark.asyncio
async def test_geosuggest_bad_request():
    result = await GeosuggestYandex.request("dddaeEeefGlklGldHghg")
    assert len(result) == 0

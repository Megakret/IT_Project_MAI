import pytest
from api.geosuggest.geosuggest import Geosuggest


@pytest.mark.asyncio
async def test_geosuggest_normal_request():
    result = await Geosuggest.request("Метрополис")
    assert len(result) > 0


@pytest.mark.asyncio
async def test_geosuggest_bad_request():
    result = await Geosuggest.request("dddaeEeefGlklGldHghg")
    assert len(result) == 0

import pytest
from api.gpt.GptCommandSuggest import GptCommand


@pytest.mark.asyncio
async def test_request_add_place():
    commander = GptCommand()
    assert await commander.command_NAC("Добавить место") == "/add_place"
    assert await commander.command_NAC("место добавь мне") == "/add_place"
    assert await commander.command_NAC("добавление места") == "/add_place"
    assert await commander.command_NAC("добавь мне место") == "/add_place"


@pytest.mark.asyncio
async def test_request_place_list():
    commander = GptCommand()
    assert await commander.command_NAC("покажи места") == "/place_list"
    assert await commander.command_NAC("список мест") == "/place_list"
    assert await commander.command_NAC("места покажи") == "/place_list"
    assert await commander.command_NAC("места") == "/place_list"


@pytest.mark.asyncio
async def test_request_get_place():
    commander = GptCommand()
    assert await commander.command_NAC("получить место") == "/get_place"
    assert await commander.command_NAC("найди мне место") == "/get_place"
    assert await commander.command_NAC("поиск мест") == "/get_place"
    assert await commander.command_NAC("место") == "/get_place"


@pytest.mark.asyncio
async def test_request_get_place_by_tags():
    commander = GptCommand()
    assert await commander.command_NAC("найди место по тегу") == "/places_by_tag"
    assert await commander.command_NAC("ресторан") == "/places_by_tag"
    assert await commander.command_NAC("торговый центр") == "/places_by_tag"
    assert await commander.command_NAC("по типу давай искать места") == "/places_by_tag"
    assert await commander.command_NAC("найти мне кафе") == "/places_by_tag"


@pytest.mark.asyncio
async def test_request_user_list():
    commander = GptCommand()
    assert await commander.command_NAC("покажи мне мои места") == "/user_place_list"
    assert (
        await commander.command_NAC("какие места я уже посетил?") == "/user_place_list"
    )
    assert await commander.command_NAC("посещенные места") == "/user_place_list"
    assert await commander.command_NAC("места мои") == "/user_place_list"
    assert (
        await commander.command_NAC("места, которые были посещены мною")
        == "/user_place_list"
    )


@pytest.mark.asyncio
async def test_error():
    commander = GptCommand()
    assert await commander.command_NAC("купи яиц") == "/error"
    assert await commander.command_NAC("Тимур") == "/error"
    assert await commander.command_NAC("Яндекс") == "/error"
    assert await commander.command_NAC("fadsfasdfdasf") == "/error"
    assert await commander.command_NAC("/admin_panel") == "/error"

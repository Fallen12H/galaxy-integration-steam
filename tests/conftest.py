from unittest.mock import MagicMock

import pytest
from galaxy.unittest.mock import AsyncMock, async_return_value
from plugin import SteamPlugin


@pytest.fixture
def backend_client():
    mock = MagicMock(spec=())
    mock.get_profile = AsyncMock()
    mock.get_profile_data = AsyncMock()
    mock.get_games = AsyncMock()
    mock.get_achievements = AsyncMock()
    mock.get_friends = AsyncMock()
    mock.get_authentication_data = AsyncMock()
    mock.set_cookie_jar = MagicMock()
    mock.set_auth_lost_callback = MagicMock()
    mock.set_cookies_updated_callback = MagicMock()
    mock.get_servers = AsyncMock()
    mock.get_owned_ids = AsyncMock()
    mock.get_steamcommunity_response_status = AsyncMock()
    return mock

@pytest.fixture
def steam_client():
    mock = MagicMock(spec=())
    mock.start = AsyncMock()
    mock.close = AsyncMock()
    mock.wait_closed = AsyncMock()
    mock.run = AsyncMock()
    mock.get_friends_info = AsyncMock()
    mock.get_friends = AsyncMock()
    mock.get_friends_nicknames = AsyncMock()
    mock.refresh_game_stats = AsyncMock()
    mock.communication_queues = {'plugin': AsyncMock(), 'websocket': AsyncMock()}
    return mock

@pytest.fixture()
async def create_plugin(backend_client, steam_client, mocker):
    created_plugins = []

    def function():
        writer = MagicMock(name="stream_writer")
        writer.drain.side_effect = lambda: async_return_value(None)

        mocker.patch("plugin.SteamHttpClient", return_value=backend_client)
        mocker.patch("plugin.WebSocketClient", return_value=steam_client)
        mocker.patch("plugin.local_games_list", return_value=[])
        plugin = SteamPlugin(MagicMock(), writer, None)
        created_plugins.append(plugin)
        return plugin

    yield function

    for plugin in created_plugins:
        plugin.close()
        await plugin.wait_closed()


@pytest.fixture()
async def plugin(create_plugin):
    return create_plugin()


@pytest.fixture()
def steam_id():
    return 123


@pytest.fixture()
def login():
    return "tester"


@pytest.fixture()
def miniprofile():
    return 123


@pytest.fixture()
async def create_authenticated_plugin(create_plugin, backend_client, mocker):
    async def function(steam_id, login, miniprofile, cache):
        plugin = create_plugin()
        plugin._user_info_cache.initialized.wait = AsyncMock()
        backend_client.get_profile.return_value = "http://url"
        backend_client.get_profile_data.return_value = steam_id, miniprofile, login
        credentials = {"account_id":"MTIz",
                       "account_username":"YWJj",
                       "persona_name":"YWJj",
                       "sentry":"Y2Jh",
                       "steam_id":"MTIz",
                       "token":"Y2Jh"}
        plugin.handshake_complete()
        await plugin.authenticate(credentials)

        return plugin

    return function


@pytest.fixture()
async def authenticated_plugin(create_authenticated_plugin, steam_id, login, miniprofile):
    return await create_authenticated_plugin(steam_id, login, miniprofile, {})




"""Some mock objects and methods to fake third party APIs."""

from tests.data.slack_api import channels, users
from tests.data.poolbot_api import player as player_data


class MockedResponse(object):

    def __init__(self, json, status_code=200):
        self.json_data = json
        self.status_code = status_code

    def json(self):
        """Mock the `.json()` method on the requests lib response object."""
        return self.json_data


def mocked_get_api(url):
    """Based off the URL return some data to mock the `api/` endpoint."""
    data = {
        'http://test-server.com/api/player/': player_data.PLAYER_LIST_RESP,
        'http://test-server.com/api/player/U1111111111/': player_data.PLAYER_1,
        'http://test-server.com/api/player/U2222222222/': player_data.PLAYER_2,
        'http://test-server.com/api/player/U3333333333/': player_data.PLAYER_3,
        'http://test-server.com/api/player/U4444444444/': player_data.PLAYER_4,
    }[url]
    return MockedResponse(json=data)


def mocked_post_api(url, data):
    """Based off the URL return some data to mock the `api/match` endpoint."""
    data = {
        'http://test-server.com/api/match/': {
            'winner': data['winner'],
            'loser': data['loser'],
        }
    }[url]
    return MockedResponse(json=data, status_code=201)


def mocked_slack_client(method):
    """Mocked response from the slack client to avoid HTTP requests."""
    return {
        'channels.list': channels.CHANNEL_LIST,
        'users.list': users.USER_LIST
    }[method]


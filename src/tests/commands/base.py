import mock
import os
import unittest

from poolbot import PoolBot

from tests.mock import (
    mocked_get_api,
    mocked_post_api,
    mocked_slack_client,
)


class BaseCommandTestCase(unittest.TestCase):

    def setUp(self):
        """Configure poolbot with the test settings and mocked 3rd party API."""
        super(BaseCommandTestCase, self).setUp()

        self.session_get_patcher = mock.patch(
            'poolbot.Session.get',
            side_effect=mocked_get_api
        )
        self.mock_player_api = self.session_get_patcher.start()

        self.session_post_patcher = mock.patch(
            'poolbot.Session.post',
            side_effect=mocked_post_api
        )
        self.mock_player_api = self.session_post_patcher.start()

        self.slack_patcher = mock.patch(
            'poolbot.SlackClient.api_call',
            side_effect=mocked_slack_client
        )
        self.mock_api = self.slack_patcher.start()

        dir_path = os.path.dirname(os.path.realpath(__file__))
        parent_dir = os.path.dirname(dir_path)
        config_path = os.path.join(parent_dir, 'config.yaml')
        self.poolbot = PoolBot(config_path=config_path)

"""Pool focused slack bot which interacts via a RTM websocket."""

import os
import inspect
import importlib
import logging
from requests import Session
from time import sleep
from urlparse import urljoin
import yaml

from slackclient import SlackClient

from models import User
from utils import MissingConfigurationException, flatten_nested_dict


logging.basicConfig(filename='poolbot.log')


class PoolBot(object):
    """Records pool results and much more using a custom slack bot."""

    PLUGIN_DIRS = ('commands', 'reactions')
    REQUIRED_SETTINGS = ('api_token', 'bot_id', 'server_host', 'server_token')

    def __init__(self, config_path='config.yaml'):
        self.config_path = config_path

        # load config settings from yaml file
        self.load_config()

        # connect to the slack websocket
        self.client = SlackClient(self.api_token)

        # initalize a session with default authorization headers
        self.prepare_requests_session()

        # save all the channels poolbot is in, and all users into memory
        self.store_poolbot_channels()
        self.store_users()

        # load all command and reaction handlers, and do pre processing work
        self.load_handlers()

        # because we will compare it regularly, cache the bot mention string
        self.bot_mention = '<@{bot_id}>'.format(bot_id=self.bot_id)

    def load_config(self):
        """Load the configuration settings from a YAML file."""
        try:
            with open(self.config_path, 'r') as f:
                self.config = yaml.load(f)
        except IOError:
            raise MissingConfigurationException(
                    'A {} file must be present in the app directory'.format(
                        self.config_path
                    )
                )

        for setting in self.REQUIRED_SETTINGS:
            try:
                setattr(self, setting, self.config[setting])
            except KeyError:
                raise MissingConfigurationException(
                    'Please add a {} setting to the {} file.'.format(
                        setting,
                        self.config_path
                    )
                )

    def load_handlers(self):
        """Load and invoke all command and reaction handlers."""
        self.commands = []
        self.reactions = []

        for plugin_dir in self.PLUGIN_DIRS:
            plugin_module = importlib.import_module(plugin_dir)
            for name, obj in inspect.getmembers(plugin_module):
                if inspect.isclass(obj):
                    getattr(self, plugin_dir).append(obj(self))

        # some commands ralso equire some setup work before they can be used
        for command in self.commands:
            command.setup()

    def listen(self):
        """Establish a connection with the Slack RTM websocket and read all
        omitted messages."""
        self.client.rtm_connect()
        while True:
            for message in self.client.rtm_read():
                print message
                self.read_input(message)
                sleep(1)

    def read_input(self, message):
        """Parse each message to determine if poolbot should take an action and
        reply based on the handler rules."""
        handler = None
        logging.debug(message['text'])

        # if the message is a explicit command for poolbot, action it
        if self.command_for_poolbot(message):
            stripped_text = message['text'].lstrip(self.bot_mention).strip(': ')
            logging.debug(stripped_text)

            for command in self.commands:
                if command.match_request(stripped_text):
                    handler = command
                    message['text'] = stripped_text
                    logging.debug(handler)

                    break

        # if not an explicit command, see if any of the reaction handlers
        # are interested in the message
        else:
            for reaction in self.reactions:
                if reaction.match_request(message):
                    handler = reaction
                    break

        if handler:
            self.execute_handler(handler, message)

    def execute_handler(self, handler, message):
        """Execute a handler and all its callbacks."""
        if handler:
            reply, callbacks = handler.process_request(message)
        else:
            reply, callbacks = (None, [])

        if reply:
            channel = self.get_channel(message['channel'])
            channel.send_message(reply)

        callback_replies = self.execute_callback_replies(callbacks, message)

    def execute_callback_replies(self, callbacks, message):
        """Match any callback strings with their handlers and execute."""
        for callback in callbacks:
            message['text'] = callback
            for command in self.commands:
                if command.match_request(callback):
                    handler = command
                    self.execute_handler(handler, message)

    def command_for_poolbot(self, message):
        """Determine if the message contains a command for poolbot."""
        # check poolbot was explicitly mentioned
        if message['user'] in self.config['nfc_bots']:
            return True

        if not message.get('text', '').startswith(self.bot_mention):
            return False

        return True

    def get_channel(self, channel_id):
        """Retrieve the channel instance based on the ID provided."""
        channels = self.client.server.channels
        bot_channel_ids = [channel.id for channel in channels]
        index = bot_channel_ids.index(channel_id)
        return self.client.server.channels[index]

    def store_poolbot_channels(self):
        """Store all the channels where poolbot is an existing member."""
        all_channels = self.client.api_call('channels.list')
        self.poolbot_channels = {
            channel['id']: channel for
            channel in all_channels['channels'] if
            channel['is_member']
        }

    def store_users(self):
        """Store details of all team members in persistent server side
        storage, and cache the user objects in memory for later reference."""
        # get all users currently stored in the datastore
        player_api_url = self.generate_url('api/player/')
        response = self.session.get(player_api_url)

        # we want to cache the players profile returned from the API so we
        # have quick local access to the elo score and total win/loss count
        player_profiles = {
            player['slack_id']: player for player in response.json()
        }

        self.users = {}
        all_users = self.client.api_call('users.list')
        if all_users['ok']:
            for user in all_users['members']:
                # annoying slackbot does not have is_bot set as True
                if user['name'] == 'slackbot' or user.get('is_bot', False):
                    continue

                user_id = user['id']

                # cache all users in memory too with their player profile
                # posting data to the server if it does not yet exist
                try:
                    player_profile = player_profiles[user_id]
                except KeyError:
                    response = self.session.post(
                        player_api_url,
                        data={
                            'name': user['name'],
                            'slack_id': user_id,
                        }
                    )
                    player_profile = response.json()

                # cache all users in memory too with their player profile
                user_profile = flatten_nested_dict(user)
                user_profile.update(player_profile)
                self.users[user_id] = User(**user_profile)

    def get_username(self, user_id, capitalize=True):
        """Fetch the user name for a slack user given their ID from the in
        memory dictionary of registered users."""
        username = self.users.get(user_id).username
        return username.title() if capitalize else username

    def get_player_profile(self, user_id):
        """Fetch the cached player profile."""
        return self.users[user_id]

    def set_player_profile(self, user_id, data):
        """Set the cache player profile, capitalizing the name for messages."""
        user = self.users[user_id]
        user.update_from_dict(data)

    def generate_url(self, path):
        """Join the host portion of the URL with the provided path."""
        return urljoin(self.server_host, path)

    def prepare_requests_session(self):
        self.session = Session()
        self.session.headers.update(
            {'Authorization': 'Token {token}'.format(token=self.server_token)}
        )

    def _get_leaderboard(self, season=True):
        """
        Retrieves current players positions ordered by their elo score.

        By default this uses the season based elo total, but the overall
        elo count can be used instead by passing season=False.
        """
        elo_field = 'season_elo' if season else 'total_elo'
        all_users_elo = {
            user.slack_id: getattr(user, elo_field) for
            user_id, user in self.users.iteritems() if
            user.included_in_leaderboard
        }

        return sorted(all_users_elo, key=all_users_elo.get, reverse=True)

    def get_leaderboard_position(self, player):
        """Retrieves position for given player"""
        try:
            return self._get_leaderboard().index(player) + 1
        except ValueError:
            # this probably means that the user ID was not returned in the 
            # ordered list of leaderboard players because they are have played
            # a game yet...
            return None


if __name__ == '__main__':
    bot = PoolBot()
    bot.listen()

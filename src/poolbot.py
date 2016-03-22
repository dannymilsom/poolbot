"""Pool focused slack bot which interacts via a RTM websocket."""

import requests
from time import sleep
from urlparse import urljoin
import yaml

from slackclient import SlackClient

from commands import command_handlers
from reactions import reaction_handlers
from utils import MissingConfigurationException


class PoolBot(object):
    """Records pool results and much more using a custom slack bot."""

    CONFIG_FILENAME = 'config.yaml'
    REQUIRED_SETTINGS = ('api_token', 'bot_id', 'server_host', 'server_token')

    def __init__(self):
        # load config settings from yaml file
        self.load_config()

        # load all command and reaction handlers
        self.load_handlers()

        # connect to the slack websocket
        self.client = SlackClient(self.api_token)

        # save all the channels poolbot is in, and all users into memory
        self.store_poolbot_channels()
        self.store_users()

        # because we will compare it regularly, cache the bot mention string
        self.bot_mention = '<@{bot_id}>:'.format(bot_id=self.bot_id)

    def load_config(self):
        """Load the configuration settings from a YAML file."""
        try:
            with open(self.CONFIG_FILENAME, 'r') as f:
                self.config = yaml.load(f)
        except IOError:
            raise MissingConfigurationException(
                    'A {} file must be present in the app directory'.format(
                        self.CONFIG_FILENAME
                    )
                )

        for setting in self.REQUIRED_SETTINGS:
            try:
                setattr(self, setting, self.config[setting])
            except KeyError:
                raise MissingConfigurationException(
                    'Please add a {} setting to the {} file.'.format(
                        setting,
                        self.CONFIG_FILENAME
                    )
                )

    def load_handlers(self):
        """Load and invoke all command and reaction handlers."""
        self.commands = [command(self) for command in command_handlers]
        self.reactions = [reaction(self) for reaction in reaction_handlers]

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

        # if the message is a explicit command for poolbot, action it
        if self.command_for_poolbot(message):
            stripped_text = message['text'].lstrip(self.bot_mention).strip()
            for command in self.commands:
                if command.match_request(stripped_text):
                    handler = command
                    break

        # if not an explicit command, see if any of the reaction handlers
        # are interested in the message
        else:
            for reaction in self.reactions:
                if reaction.match_request(message):
                    handler = reaction
                    break

        reply = handler.process_request(message) if handler else None

        if reply is not None:
            channel = self.get_channel(message['channel'])
            channel.send_message(reply)

    def command_for_poolbot(self, message):
        """Determine if the message contains a command for poolbot."""
        # check poolbot was explicitly mentioned
        if not message.get('text', '').startswith(self.bot_mention):
            return False

        # verify poolbot is in the channel where the message was posted
        return message.get('channel') in self.poolbot_channels

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
        response = requests.get(player_api_url)
        stored_ids = [user['slack_id'] for user in response.json()]

        self.users = {}
        all_users = self.client.api_call('users.list')
        if all_users['ok']:
            for user in all_users['members']:
                # annoying slackbot does not have is_bot set as True
                if user['name'] == 'slackbot' or user['is_bot']:
                    continue

                # cache all users in memory too
                self.users[user['id']] = user

                if user['id'] not in stored_ids:
                    requests.post(
                        player_api_url,
                        data={
                            'name': user['name'],
                            'slack_id': user['id']
                        }
                    )

    def store_user(self, user_id):
        """Store a single user in the server side datastore."""
        user_details = self.client.api_call('users.info', user=user_id)
        url = self.generate_url('api/player')
        response = requests.post(
            url,
            data={
                'name': user_details['user']['name'],
                'slack_id': user_details['user']['id']
            }
        )

    def generate_url(self, path):
        """Join the host portion of the URL with the provided path."""
        return urljoin(self.server_host, path)


if __name__ == '__main__':
    bot = PoolBot()
    bot.listen()

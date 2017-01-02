from handler import Handler
from utils import get_ordinal_extension


class ChannelJoinReaction(Handler):
    """Welcome new users to the channel with poolbot monitoring messages."""

    url_path = 'api/player/'

    def match_request(self, message):
        """Look for a message to represent a player joining the channel."""
        return message.get('subtype') == 'channel_join'

    def process_request(self, message):
        """Find the message author ID, add them to the datastore if not already
        registered and return a welcome message."""
        user_id = message['user']

        # add the user to the users list if not already saved
        if user_id not in self.poolbot.users:
            response = self.poolbot.session.post(
                self._generate_url(),
                data={
                    'name': message['user_profile']['name'],
                    'slack_id': user_id
                }
            )

            # create a local version of the user in the cache
            player_profile = response.json()
            
            user_profile = flatten_nested_dict(message['user_profile'])
            user_profile.update(player_profile)
            self.poolbot.users[user_id] = User(**user_profile)

            # generate our reply for the new user
            return self.reply(
                'Welcome to the baze {name}! :wave:'.format(
                    name=self.poolbot.users[user_id].username
                ),
                callbacks=['help']
            )

        # if the user is already recognised get their leaderboard position
        position = self.poolbot.get_leaderboard_position(message['user'])
        username = self.poolbot.users[user_id].username

        if position is None:
            callbacks = []
            msg = 'Welcome home {name}! :wave:'.format(name=username)
        else:
            callbacks = ['stats']
            msg = 'Welcome back {name}! :wave: You currently hold {position} place in this seasons leaderboard!'.format(
                name=username,
                position=get_ordinal_extension(position)
            )
        return self.reply(msg, callbacks=callbacks)

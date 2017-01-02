from handler import Handler
from utils import get_ordinal_extension


class ChannelLeaveReaction(Handler):
    """Say goodbye to users when they leave the room."""

    def match_request(self, message):
        return message.get('subtype') == 'channel_leave'

    def process_request(self, message):
        """
        Return the leaving users leaderboard position and
        calls the stats command for extra data.
        """
        position = self.poolbot.get_leaderboard_position(message['user'])

        # try and get the cached user profile
        user_profile = self.poolbot.users.get(message['user'])
        if user_profile is None:
            username = message['user_profile']['name'].title()
        else:
            username = user_profile.username

        if position is None:
            callbacks = []
            msg = "Goodbye {name}. You'll be back! :crystal_ball:".format(
                name=username
            )
        else:
            callbacks = ['stats']
            msg = "{name} has left holding {position} position in the leaderboard. :eyes:".format(
                name=username,
                position=get_ordinal_extension(position)
            )

        return self.reply(msg, callbacks=callbacks)

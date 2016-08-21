from .base import BaseCommand


class StatsCommand(BaseCommand):
    """Returns some interesting statistics about a player."""

    command_term = 'stats'
    url_path = 'api/player/{user_id}/'
    help_message = (
        'The stats command returns interesting statistics about each player. '
        'You can explicitly pass a player name, or just type `@poolbot stats` '
        'to retrieve your own stats.'
    )
    response_msg = (
        '{name} has played {total_match_count} games '
        '(E {elo} / W {total_win_count} / L {total_loss_count})'
    )

    def process_request(self, message):
        try:
            user_id = self._find_user_mentions(message['text'])[0]
        except IndexError:
            user_id = message['user']

        # try to use the cached player profile, falling back to the API
        try:
            return self.reply(self._generate_response_from_cache(user_id))
        except KeyError:
            return self.reply(self._generate_response_from_api(user_id))

    def _generate_response_from_api(self, user_id):
        """Parse the API data and transform it into a human readable message."""
        response = self.poolbot.session.get(
            self._generate_url(user_id=user_id)
        )
        if response.status_code == 200:
            data = response.json()
            return self.response_msg.format(**data)
        else:
            return 'Sorry, I was unable to fetch that data.'

    def _generate_response_from_cache(self, user_id):
        """Construct the reply from the cached profile data."""
        player_profile = self.poolbot.get_player_profile(user_id)
        return self.response_msg.format(**player_profile)

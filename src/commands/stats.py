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
        '{name} has played {total_match_count} games overall '
        '(E {total_elo} / W {total_win_count} / L {total_loss_count}) .'
        'This season they have played {season_match_count} games '
        '(E {season_elo} / W {season_win_count} / L {season_loss_count}).'
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
        """Construct the reply from the cached user instace."""
        user = self.poolbot.users[user_id]
        return self.response_msg.format(
            name=user.username,
            total_elo=user.total_elo,
            total_match_count=user.total_match_count,
            total_win_count=user.total_win_count,
            total_loss_count=user.total_loss_count,
            season_elo=user.season_elo,
            season_match_count=user.season_match_count,
            season_win_count=user.season_win_count,
            season_loss_count=user.season_loss_count,
        )

from .base import BaseCommand


class StatsCommand(BaseCommand):
    """Returns some interesting statistics."""

    command_term = 'stats'
    url_path = 'api/player/{user_id}/'

    def process_request(self, message):
        try:
            user_id = self._find_user_mentions(message)[0]
        except IndexError:
            user_id = message['user']

        response = self.poolbot.session.get(self._generate_url(user_id=user_id))

        if response.status_code == 200:
            return self._generate_response(response.json())
        else:
            return 'Sorry, I was unable to fetch that data.'

    def _generate_response(self, data):
        """Parse the returned data and transform it into a human readable
        message."""
        player_name = data['name']
        win_count = data['total_win_count']
        loss_count = data['total_loss_count']
        game_count = win_count + loss_count

        return (
            '{player} has played {game_count} games, recording {win_count} '
            'wins and {loss_count} loses.'.format(
                player=player_name.title(),
                game_count=game_count,
                win_count=win_count,
                loss_count=loss_count
            )
        )

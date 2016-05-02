from .base import BaseCommand


class LeaderboardCommand(BaseCommand):
    """Returns a leadboard of players, ordered by their wins."""

    default_limit = 10
    command_term = 'leaderboard'
    url_path = 'api/player/'
    help = (
        'Use the `leadboard` command to see which player has won the most overall games.'
    )

    def process_request(self, message):
        """Get the recent match results for the user mentioned in the text."""
        leaderboard_url = self._generate_url()

        get_params = {'ordering': '-total_wins_field'}
        response = self.poolbot.session.get(
            leaderboard_url,
            params=get_params,
        )

        if response.status_code == 200:
            limit = self._calculate_limit(message)
            players_to_include = response.json()[:limit]
            return self._generate_response(players_to_include)
        else:
            return 'Unable to get leadboard data'

    def _calculate_limit(self, message):
        """Parse the message to see if an additional parameter was passed
        to limit the number of players shown in the leaderboard. If no arg
        is passed, or the arg cannot be cast to an integer, default to 10.
        """
        limit = self.default_limit
        args = self._command_args(message)
        if len(args) > 1:
            try:
                limit = int(args[1])
            except ValueError:
                pass
        return limit

    def _generate_response(self, data):
        """Parse the returned data and generate a string which takes the form
        of a leaderboard style table, with players ranked from 1 to X.
        """
        leaderboard_row_msg = '{ranking}. {name} ({wins} wins)'
        leaderboard_table_rows = [
            leaderboard_row_msg.format(
                ranking=i,
                name=player['name'],
                wins=player['total_win_count'],
            ) for i, player in enumerate(data, 1)
        ]
        return ' \n'.join(leaderboard_table_rows)

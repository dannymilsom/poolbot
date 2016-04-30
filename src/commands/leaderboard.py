import requests

from .base import BaseCommand


class LeaderboardCommand(BaseCommand):
    """Returns a leadboard of players, ordered by their wins."""

    command_term = 'leaderboard'
    url_path = 'api/player/'
    help = (
        'Use the `leadboard` command to see which player has won the most overall games.'
    )

    def process_request(self, message):
        """Get the recent match results for the user mentioned in the text."""
        leaderboard_url = self._generate_url()

        get_params = {'ordering': '-total_wins_field'}
        response = requests.get(
            leaderboard_url,
            params=get_params,
            headers=self.poolbot.get_request_headers()
        )

        if response.status_code == 200:
            return self._generate_response(response.json())
        else:
            return 'Unable to get leadboard data'


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

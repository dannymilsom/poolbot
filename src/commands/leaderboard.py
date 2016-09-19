from .base import BaseCommand


class LeaderboardCommand(BaseCommand):
    """Returns a leadboard of players, ordered by their wins."""

    default_limit = 10
    default_elo_field = 'season'
    command_term = 'leaderboard'
    url_path = 'api/player/'
    help_message = (
        'The leadboard command returns a table of users ranking by their raw '
        'win count. You can pass `season` or `all` in the command to determine '
        'which elo points score should be used. If no additional argument is '
        'passed, the season elo score is default.'
    )

    def process_request(self, message):
        """Get the elo scores via the API and format to form the leaderboard."""
        self.elo_field = self._determine_elo_field(message)

        leaderboard_url = self._generate_url()
        get_params = {
            'active': True,
            'ordering': '-{}_elo'.format(self.elo_field)
        }
        response = self.poolbot.session.get(
            leaderboard_url,
            params=get_params,
        )

        if response.status_code == 200:
            limit = self._calculate_limit(message)
            return self.reply(self._generate_response(response.json(), limit))
        else:
            return self.reply('Unable to get leadboard data')

    def _determine_elo_field(self, message):
        """Determine which elo ranking field to use."""
        args = self._command_args(message)
        if args and args[0] == 'all':
            elo_field = 'total'
        else:
            elo_field = self.default_elo_field
        return elo_field

    def _calculate_limit(self, message):
        """Parse the message to see if an additional parameter was passed
        to limit the number of players shown in the leaderboard. If no arg
        is passed, or the arg cannot be cast to an integer, default to 10.
        """
        args = self._command_args(message)
        for arg in args:
            try:
                return int(arg)
            except ValueError:
                pass
        return self.default_limit

    def _generate_response(self, data, limit):
        """Parse the returned data and generate a string which takes the form
        of a leaderboard style table, with players ranked from 1 to X.
        """
        leaderboard_row_msg = '{ranking}. {name} [Elo Score: {elo}] ({wins} W / {losses} L)'
        leaderboard_table_rows = []

        for player in data:  # Go through list
            if player['{}_win_count'.format(self.elo_field)] or player['{}_loss_count'.format(self.elo_field)]:  # See if user has played any games
                leaderboard_table_rows.append(leaderboard_row_msg.format(
                    ranking=len(leaderboard_table_rows) + 1,
                    name=player['name'],
                    wins=player['{}_win_count'.format(self.elo_field)],
                    losses=player['{}_loss_count'.format(self.elo_field)],
                    elo=player['{}_elo'.format(self.elo_field)])
                )

        # finally only return the rows we actually want
        return ' \n'.join(leaderboard_table_rows[:limit])

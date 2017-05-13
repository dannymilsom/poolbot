from .base import BaseCommand


class LeaderboardCommand(BaseCommand):
    """Returns a leadboard of players, ordered by their elo points."""

    default_limit = 10
    default_elo_field = 'season'
    command_term = 'leaderboard'
    url_path = 'api/player/'
    help_message = (
        'The leadboard command returns a table of users ranking by their elo '
        'points. You can pass `season` or `all` in the command to determine '
        'which elo points score should be used. If no additional argument is '
        'passed, the season elo score is default. To reduce the length of the '
        'leaderboard displayed, you can pass an additional integer argument. '
        'To only include players who have played more than ten games, pass the'
        '`minimum` argument.'
    )

    def process_request(self, message):
        """Get the elo scores via the API and format to form the leaderboard."""
        command_args = self._command_args(message, include_user_mentions=False)
        self.elo_field = self._determine_elo_field(command_args)

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
            limit = self._calculate_limit(command_args)
            minimum = self._minimum_games_filter(command_args)
            return self.reply(
                self._generate_response(response.json(), limit, minimum)
            )
        else:
            return self.reply('Unable to get leadboard data')

    def _determine_elo_field(self, command_args):
        """Determine which elo ranking field to use."""
        return 'total' if 'all' in command_args else self.default_elo_field

    def _calculate_limit(self, command_args):
        """Parse the message to see if an additional parameter was passed
        to limit the number of players shown in the leaderboard. If no arg
        is passed, or the arg cannot be cast to an integer, default to 10.
        """
        for arg in command_args:
            try:
                return int(arg)
            except ValueError:
                pass
        return self.default_limit

    def _minimum_games_filter(self, command_args):
        """Determine if an argument was passed to filter the leaderboard to
        only include players who have played a minimum number of games.
        """
        return 10 if 'minimum' in command_args else 1

    def _generate_response(self, data, limit, minimum_games=1):
        """Parse the returned data and generate a string which takes the form
        of a leaderboard style table, with players ranked from 1 to X.
        """
        leaderboard_row_msg = '{ranking}. {name} [Elo Score: {elo}] ({wins} W / {losses} L)'
        leaderboard_table_rows = []

        for player in data:
            if (
                player['{}_win_count'.format(self.elo_field)] >= minimum_games or
                player['{}_loss_count'.format(self.elo_field)] >= minimum_games
            ):
                leaderboard_table_rows.append(leaderboard_row_msg.format(
                    ranking=len(leaderboard_table_rows) + 1,
                    name=player['name'],
                    wins=player['{}_win_count'.format(self.elo_field)],
                    losses=player['{}_loss_count'.format(self.elo_field)],
                    elo=player['{}_elo'.format(self.elo_field)])
                )

        # finally only return the rows we actually want
        return ' \n'.join(leaderboard_table_rows[:limit])

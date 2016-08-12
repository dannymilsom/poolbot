from operator import itemgetter

from .base import BaseCommand

from utils import format_datetime_to_date


class GrannyCommand(BaseCommand):
    """Returns a leadboard of grannies, ordered by the most grannies given."""

    default_limit = 10
    command_term = 'grannies'
    url_path = 'api/player/'
    help_message = (
        'The leadboard command returns a table of users ranking by the number '
        'of grannies they have handed out.'
    )

    def process_request(self, message):
        """Hit the players API to get all player profile data."""
        try:
            user_id = self._find_user_mentions(message)[0]
        except IndexError:
            return self._get_granny_leaderboard(message)
        else:
            return self._get_player_grannies(user_id)

    def _get_player_grannies(self, user_id):
        """Get the details of all grannies a player has given / recieved."""
        granny_url = (
            '{player_url}{player}/grannies/'.format(
                player_url=self.url_path,
                player=user_id
            )
        )
        response = self.poolbot.session.get(
            self.poolbot.generate_url(granny_url)
        )

        if response.status_code == 200:
            data = response.json()
            return self._generate_player_granny_response(user_id, data)
        else:
            return 'Unable to get player granny data'

    def _get_granny_leaderboard(self, message):
        """Return a table sorted by grannies given."""
        players_url = self._generate_url()
        get_params = {
            'active': True,
            'ordering': '-total_grannies_given_count'
        }
        response = self.poolbot.session.get(
            players_url,
            params=get_params,
        )

        if response.status_code == 200:
            limit = self._calculate_limit(message)
            return self._generate_response(response.json(), limit)
        else:
            return 'Unable to get granny data'

    def _calculate_limit(self, message):
        """Parse the message to see if an additional parameter was passed
        to limit the number of players shown in the granny table. If no arg
        is passed, or the arg cannot be cast to an integer, default to 10.
        """
        limit = self.default_limit
        args = self._command_args(message)
        if args:
            try:
                limit = int(args[0])
            except ValueError:
                pass
        return limit

    def _generate_player_granny_response(self, user_id, matches):
        """Format a response listing all matches where a granny is recorded."""
        ordered_matches = sorted(matches, key=itemgetter('date'), reverse=True)
        match_template = '{data}: {winner} grannied {loser}'
        formatted_matches = [
            match_template.format(
                data=format_datetime_to_date(match['date']),
                winner=self.poolbot.get_username(match['winner']),
                loser=self.poolbot.get_username(match['loser'])
            ) for match in ordered_matches
        ]
        all_matches = "\n".join(formatted_matches)

        resp_str = (
            '{player} has recorded {grannies_given} grannies and '
            'taken {grannies_taken}: ```\n{matches}\n```'
        )

        player_profile = self.poolbot.get_player_profile(user_id)
        return resp_str.format(
            player=self.poolbot.get_username(user_id),
            grannies_given=player_profile['total_grannies_given_count'],
            grannies_taken=player_profile['total_grannies_taken_count'],
            matches=all_matches
        )

    def _generate_response(self, data, limit):
        """Parse the returned data and generate a string which takes the form
        of a leaderboard style table, with players ranked from 1 to X.
        """
        table_row_msg = (
            '{ranking}. {name} ({grannies_given} G / {grannies_taken} T)'
        )
        table_rows = []

        for player in data:
            if player['total_win_count'] or player['total_loss_count']:
                table_rows.append(table_row_msg.format(
                    ranking=len(table_rows) + 1,
                    name=player['name'],
                    grannies_given=player['total_grannies_given_count'],
                    grannies_taken=player['total_grannies_taken_count'])
                )

        # finally only return the rows we actually want
        return ' \n'.join(table_rows[:limit])

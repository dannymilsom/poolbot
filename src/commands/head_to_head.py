from datetime import datetime
import random
from operator import itemgetter

from utils import format_datetime_to_date
from .base import BaseCommand


class HeadToHeadCommand(BaseCommand):
    """Return the results of the previous games between two players."""

    command_term = 'head-to-head'
    url_path = 'api/match/head_to_head/'
    help_message = (
        'Use the `head-to-head` command to see all results between two players. '
        'For example, `@poolbot head-to-head @danny @marin` will return number '
        'of wins for each player, and the details of their last five matches. '
        'If you want to see the head-to-head between yourself and another '
        'player, passing your own name is optional.'
    )

    def process_request(self, message):
        mentioned_user_ids = self._find_user_mentions(message)
        if not len(mentioned_user_ids):
            return 'Sorry, I was unable to find two users in that message...'

        try:
            player1 = mentioned_user_ids[0]
            player2 = mentioned_user_ids[1]
        except IndexError:
            player2 = message['user']

        response = self.poolbot.session.get(
            self._generate_url(),
            params={
                'player1': player1,
                'player2': player2,
            }
        )

        if response.status_code == 200:
            data = response.json()
            player1_wins = data[player1]
            player2_wins = data[player2]
            total_games = player1_wins + player2_wins
            most_wins = player1 if player1_wins > player2_wins else player2
            most_loses = player2 if most_wins == player1 else player1

            reply_text = (
                '{winner} has won {winner_win_count} games. '
                '{loser} has only won {loser_win_count}! '
                'This gives a win ratio of {winner_ratio} for {winner}! '
                'The last {recent_game_count} results were:'
                '```\n{recent_games}\n```'
            )

            try:
                winning_percentage = ((data[most_wins] * 100) / total_games)
            except ZeroDivisionError:
                return (
                    '{player1} and {player2} are yet to record any games!'.format(
                        player1=self.poolbot.get_username(player1),
                        player2=self.poolbot.get_username(player2)
                    )
                )

            return reply_text.format(
                winner=self.poolbot.get_username(most_wins),
                loser=self.poolbot.get_username(most_loses),
                winner_win_count=data[most_wins],
                loser_win_count=data[most_loses],
                winner_ratio='{percent:.0f}%'.format(percent=winning_percentage),
                recent_game_count=data['history_count'],
                recent_games=self._format_recent_matches(data['history'])
            )
        else:
            return 'Sorry, I was unable to get head to head data!'

    def _format_recent_matches(self, matches):
        ordered_matches = sorted(matches, key=itemgetter('date'), reverse=True)
        match_template = '{data}: {winner} beat {loser}'
        formatted_matches = [
            match_template.format(
                data=format_datetime_to_date(match['date']),
                winner=self.poolbot.get_username(match['winner']),
                loser=self.poolbot.get_username(match['loser'])
            ) for match in ordered_matches
        ]
        return "\n".join(formatted_matches)


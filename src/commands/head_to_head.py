import requests
import random

from .base import BaseCommand


class HeadToHeadCommand(BaseCommand):
    """Return the results of the previous games between two players."""

    command_term = 'head-to-head'
    url_path = 'api/match/head_to_head/'
    shame_adjectives = (
        'awkward',
        'distressing',
        'embarrassing',
        'shameful',
        'troubling',
    )
    help = (
        'Use the `head-to-head` command to see all results between two players.\n'
        'For example, `@poolbot head-to-head @danny @marin` will return number '
        'of wins for each player.'
    )

    def process_request(self, message):
        mentioned_user_ids = self._find_user_mentions(message)
        try:
            player1 = mentioned_user_ids[0]
            player2 = mentioned_user_ids[1]
        except IndexError:
            return 'Sorry, I was unable to find two users in that message...' 

        response = requests.get(
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
            most_wins = player1 if player1_wins > player2_wins else player2
            most_loses = player2 if most_wins == player1 else player1

            reply_text = (
                '{winner} has beaten {loser} {win_count} times - giving a win '
                'ratio of {ratio}! How {adjective} for {biggest_loser}!'
            )
            return reply_text.format(
                winner=most_wins,
                loser=most_loses,
                win_count=data[most_wins],
                ratio='{percentage:.0%}'.format(
                    percentage=float(data[most_wins]/(sum(data.values())))
                ),
                adjective=random.choice(self.shame_adjectives),
                biggest_loser=most_loses
            )
        else:
            return 'Unable to get head to head data'

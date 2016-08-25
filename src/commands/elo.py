from .base import BaseCommand


class EloCommand(BaseCommand):
    """Returns the points that can be won/lost between two players."""

    command_term = 'elo'
    url_path = 'api/player/elo/'
    help_message = (
      'The `elo` command returns the points that can be won/lost between two '
      'players.'
    )
    briefmode_flags = (
        '-brief',
        '-mini',
        '-short'
    )
    reply_message = (
        '{player} currently has elo {elo} points. A win would be worth '
        '{points_win} points, giving a new total of {elo_win}. A loss '
        'would cost them {points_lose} points reducing them to '
        '{elo_lose}.\n'
    )
    reply_message_brief = (
        '{player_1} [{player_1_elo}] vs {player_2} [{player_2_elo}]'
        'A: {player_1} > {player_2}: ± {player_1_points_win}'
        'B: {player_2} > {player_1}: ± {player_2_points_win}'
    )

    def process_request(self, message):
        mentioned_user_ids = self._find_user_mentions(message['text'])
        if not len(mentioned_user_ids):
            return self.reply('Sorry, you must mention at least one user.')

        # check if brief message mode is enabled
        brief = self._find_briefmode_flag(message['text'].lower())

        try:
            player1 = mentioned_user_ids[0]
            player2 = mentioned_user_ids[1]
        except IndexError:
            player2 = player1
            player1 = message['user']

        response = self.poolbot.session.get(
            self._generate_url(),
            params={
                'player1': player1,
                'player2': player2,
            }
        )

        if response.status_code == 200:
            data = response.json()

            ret = []

            if brief == True:
                player1 = data[0]
                player2 = data[1]
                ret.append(self.reply_message_brief.format(
                    player_1: player1['slack_id'],
                    player_2: player2['slack_id'],
                    player_1_elo: player1['elo'],
                    player_2_elo: player2['elo'],
                    player_1_points_win: player1['points_win'],
                    player_2_points_win: player2['points_win'],
                ))
            else:
                for player in data:
                    ret.append(self.reply_message.format(
                        player=self.poolbot.get_username(player['slack_id']),
                        elo=player['elo'],
                        elo_win=player['elo_win'],
                        elo_lose=player['elo_lose'],
                        points_win=player['points_win'],
                        points_lose=player['points_lose'],
                    ))

            return self.reply(' '.join(ret))
        else:
            return self.reply('Sorry, I was unable to fetch that data.')


    def _find_briefmode_flag(self, text):
        """
        Search for a brief flag in the message text.
        """
        return any(noun in text for noun in self.briefmode_flags)

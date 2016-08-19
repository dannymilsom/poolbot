from .base import BaseCommand


class EloCommand(BaseCommand):
    """Returns the points that can be won/lost between two players."""

    command_term = 'elo'
    url_path = 'api/player/elo/'
    help_message = (
      'The `elo` command returns the points that can be won/lost between two '
      'players.'
    )

    def process_request(self, message):
        mentioned_user_ids = self._find_user_mentions(message)
        if not len(mentioned_user_ids):
            return self.reply('Sorry, you must mention at least one user.')

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

            reply_text = (
                '*{player}* [E: {elo} / W: {elo_win} (+{points_win}) / '
                'L: {elo_lose} (-{points_lose})]'
            )
            ret = []

            for player in data:
                ret.append(reply_text.format(
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

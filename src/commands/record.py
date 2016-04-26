import requests

from .base import BaseCommand


class RecordCommand(BaseCommand):
    """Records the result of a match."""

    command_term = 'record'
    url_path = 'api/match/'
    victory_nouns = (
        'beat',
        'battered',
        'defeated',
        'destroyed',
        'crushed',
        'clobbered',
        'crushed',
        'defeated',
        'disgraced',
        'emasculated',
        'grilled',
        'embarrassed',
        'humiliated',
        'grannied',
        'hammered',
        'obliterated',
        'pounded',
        'trounced',
        'thrashed',
        'slayed',
        'smashed',
        'spangled',
        'walloped',
    )

    def process_request(self, message):
        """The author is always the winner."""
        try:
            defeated_player = self._find_user_mentions(message)[0]
        except IndexError:
            return 'Sorry, I was unable to find an opponent in that message...' 

        lower_text = message['text'].lower()
        if not any(noun in lower_text for noun in self.victory_nouns):
            return (
                'Sorry, I am unable to determine the result. Record a win by '
                'posting a message like `record beat @opponent`. You can '
                'replace `beat` with any word from the following list:\n'
                '`{victory_nouns}`'.format(
                    victory_nouns = ', '.join(noun for noun in self.victory_nouns)
                )
            )

        response = requests.post(
            self._generate_url(),
            data={
                'winner': message['user'],
                'loser': defeated_player,
                'channel': message['channel'],
                'granny': 'grannied' in lower_text,
            },
            headers=self.poolbot.get_request_headers()
        )

        if response.status_code == 201:
            return 'Victory recorded for {winner}!'.format(
                winner=self.poolbot.get_username(message['user'])
            )
        else:
            return 'Sorry, I was unable to record that result.'
        # TODO generate some funny phrase to celebrate the victory
        # eg highlight an unbetean run, or X consequtive lose etc

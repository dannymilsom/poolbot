import logging
import random

from .base import BaseCommand
from .record import RecordCommand


class RecordNFCCommand(BaseCommand):
    """
    This command can works only if the sender is one of the NFC bots
    """
    command_term = 'nfc-red'

    @property
    def nfc_bots(self):
        return self.poolbot.config['nfc_bots']

    def process_request(self, message):
        """
        The message author has to be one of the NFC bots (Bristol or London one).
        The winner is mentioned first, then the loser.
        """
        msg_author = message['user']
        logging.debug(self.nfc_bots)
        if msg_author not in self.nfc_bots:
            return

        winner, loser = self._find_players(message['text'])

        # Fake the record command
        record = RecordCommand()
        victory_noun = random.choice(record.victory_nouns)
        message['user'] = winner
        message['text'] = "{} <@{}>".format(victory_noun, loser)
        logging.debug(message)
        # Pretend it's a record command!
        return record.process_request(message)

    def _find_players(self, text):
        """Parses the message text and returns two user IDs: winner's and loser's."""
        return self._find_players(text)[:2]

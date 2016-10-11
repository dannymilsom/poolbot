import random

from .base import BaseCommand
from .record import RecordCommand


class RecordNFCCommand(BaseCommand):
    """
    This command can works only if the sender is one of the NFC bots
    """
    command_term = 'nfc-red:'  # TODO: now it is a proper hack! Make it nice, please!

    @property
    def nfc_bots(self):
        return self.poolbot.config['nfc_bots']

    def process_request(self, message):
        """
        The message author has to be one of the NFC bots (Bristol or London one).
        The winner is mentioned first, then the loser.
        """
        msg_author = message['bot_id']

        if msg_author not in self.nfc_bots:
            return self.reply('Only NFC bots can use this command')

        try:
            winner, loser = self._find_players(message['text'])
        except ValueError:  # safety check just in case NFC bot sends a wrong text
            return self.reply("Unable to record game via NFC.")

        # Fake the record command
        record = RecordCommand(poolbot=self.poolbot)
        victory_noun = random.choice(record.victory_nouns)
        message['user'] = winner
        message['text'] = "{} <@{}>".format(victory_noun, loser)

        # Pretend it's a record command!
        return record.process_request(message)

    def _find_players(self, text):
        """Parses the message text and returns two user IDs: winner's and loser's."""
        return self._find_user_mentions(text)[:2]

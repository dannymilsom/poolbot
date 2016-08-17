from .base import BaseCommand


class OddsCommand(BaseCommand):
    """Returns some odds based on the players and recent results."""

    command_term = 'odds'

    def process_request(self, message):
        return self.reply('Sorry this command is not implemented yet...')

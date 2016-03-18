from .base import BaseCommand


class StatsCommand(BaseCommand):
    """Returns some interesting statistics."""

    command_term = 'stats'

    def process_request(self, message):
        return 'Sorry this command is not implemented yet...'

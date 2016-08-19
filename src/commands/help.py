from .base import BaseCommand
from .form import FormCommand
from .head_to_head import HeadToHeadCommand
from .odds import OddsCommand
from .record import RecordCommand
from .stats import StatsCommand
from .elo import EloCommand


class HelpCommand(BaseCommand):
    """Returns advice on how to use the enabled poolbot commands."""

    command_term = 'help'

    def process_request(self, message):
        """Return some helper messages describing how commands work."""
        helpers = {
            command.command_term: command.help_message for
            command in self.poolbot.commands
        }

        args = self._command_args(message)
        try:
            # asking for help on how to use an explicit command
            reply = helpers[args[1]]
        except (IndexError, KeyError):
            # fallback to a general help message
            commands = '`, `'.join(sorted(helpers.keys()))
            template = (
                'Try one of these commands: `{command_list}`. For more '
                'help on how to use a command, type `@poolbot help <command>`.'
            )
            reply = template.format(command_list=commands)

        return self.reply(reply)

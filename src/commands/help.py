from .base import BaseCommand
from .form import FormCommand
from .head_to_head import HeadToHeadCommand
from .odds import OddsCommand
from .record import RecordCommand
from .stats import StatsCommand


class HelpCommand(BaseCommand):
    """Returns advice on how to use the enabled poolbot commands."""

    command_term = 'help'

    def process_request(self, message):
        all_commands = [
            FormCommand,
            HeadToHeadCommand,
            RecordCommand,
            StatsCommand,
            OddsCommand,
        ]
        helpers = {
            command.command_term: command.help for command in all_commands
        }

        # looking for messages like @poolbot help <command_term>, falling back
        # to a list of all command terms if no explicit help requsted
        text_content = self._strip_poolbot_from_message(message)
        split_text = text_content.lower().split(' ')
        try:
            reply = helpers[split_text[1]]
        except (IndexError, KeyError):
            commands_list = ', '.join(helpers.keys())
            reply = 'Try one of these commands: {command_list}'.format(
                command_list=commands_list
            )

        return reply

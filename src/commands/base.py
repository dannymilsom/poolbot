import re

from handler import Handler


class BaseCommand(Handler):

    help_message = 'No help available...'
    url_path = ''
    command_term = None
    mention_regex = '<@[a-zA-Z0-9]+>'

    def match_request(self, text):
        """Return a boolean to indicate if the message is a command directed
        at poolbot. The `@poolbot:` mention should already be stripped from the
        beginning of the text passed as an argument, to avoid the overhead of
        checking in each commands match_request() method."""
        first_word = text.strip().split(' ')[0]
        return first_word == self.command_term

    def setup(self):
        """Perform some actions when the poolbot client loads, in preperation
        for message processing."""
        pass

    def _find_user_mentions(self, text):
        """Parses the message text and returns all user ids mentioned excluding
        poolbot."""
        user_mentions = re.findall(self.mention_regex, text)
        user_ids = [mention.strip('@<>') for mention in user_mentions]
        return [user_id for user_id in user_ids if user_id != self.poolbot.bot_id]

    def _strip_poolbot_from_message(self, message):
        """Return the message text with the poolbot mention removed."""
        return message['text'].lstrip(self.poolbot.bot_mention).strip()

    def _command_args(self, message, include_command_term=False, include_user_mentions=True):
        """Return an iterable of all args passed after the poolbot mention."""
        stripped_message = self._strip_poolbot_from_message(message)
        split_message = stripped_message.split()

        # we know the first argument is going to be the command_term,
        # as we check this in the match_request() method
        if not include_command_term:
            del split_message[0]

        # sometimes we are only interested in the extra arguments
        if not include_user_mentions:
            for value in split_message[:]:
                if re.match(self.mention_regex, value):
                    split_message.remove(value)

        return split_message

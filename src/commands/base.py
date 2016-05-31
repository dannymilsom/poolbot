import re


class BaseCommand(object):

    help = ''
    url_path = ''
    command_term = None
    mention_regex = '<@[a-zA-Z0-9]+>'

    def __init__(self, poolbot):
        """Make poolbot available to all commands."""
        self.poolbot = poolbot

    def match_request(self, text):
        """Return a boolean to indicate if the message is a command directed
        at poolbot. The `@poolbot:` mention should already be stripped from the
        beginning of the text passed as an argument, to avoid the overhead of
        checking in each commands match_request() method."""
        first_word = text.strip().split(' ')[0]
        return first_word.lower().startswith(self.command_term)

    def process_request(self, message):
        """Perform the action associated with the command, and return a reply
        for poolbot to post back to the channel."""
        return NotImplemented()

    def setup(self):
        """Perform some actions when the poolbot client loads, in preperation
        for message processing."""
        pass

    def _find_user_mentions(self, message):
        """Parses the message text and returns all user ids mentioned excluding
        poolbot."""
        user_mentions = re.findall(self.mention_regex, message['text'])
        user_ids = [mention.strip('@<>') for mention in user_mentions]
        return [user_id for user_id in user_ids if user_id != self.poolbot.bot_id]

    def _generate_url(self, **kwargs):
        """Join the host portion of the URL with the provided command path."""
        path = self.url_path.format(**kwargs)
        return self.poolbot.generate_url(path)

    def _strip_poolbot_from_message(self, message):
        """Return the message text with the poolbot mention removed."""
        return message['text'].lstrip(self.poolbot.bot_mention).strip()

    def _command_args(self, message):
        """Return an iterable of all args passed after the poolbot mention."""
        stripped_message = self._strip_poolbot_from_message(message)
        return stripped_message.split()

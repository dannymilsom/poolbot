import re


class BaseReaction(object):

    url_path = ''

    def __init__(self, poolbot):
        """Make poolbot available to all reactions."""
        self.poolbot = poolbot

    def match_request(self, message):
        """Return a boolean to indicate if the message should be processed
        by this handler."""
        return NotImplemented()

    def process_request(self, message):
        """Return a message which poolbot should reply to the channel with. This
        method is only called if the match_request() method returns True."""
        return NotImplemented()

    def reply(self, message, callbacks=None):
        if callbacks is None:
            callbacks = []
        return (message, callbacks)

    def _generate_url(self, **kwargs):
        """Join the host portion of the URL with the provided command path."""
        path = self.url_path.format(**kwargs)
        return self.poolbot.generate_url(path)

    def _find_subtype_mentions(self, message):
        """Parses the message text and returns all user ids mentioned excluding
        poolbot."""
        subtype_mention_regex = '<@[a-zA-Z0-9]+|'
        user_mentions = re.findall(subtype_mention_regex, message['text'])
        user_ids = [mention.strip('@<>') for mention in user_mentions]
        return [user_id for user_id in user_ids if user_id != self.poolbot.bot_id]

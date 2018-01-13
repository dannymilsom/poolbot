class Handler(object):
    """Base class for handlers which defines the interface to implement."""

    def __init__(self, poolbot):
        """Make poolbot available to all handlers."""
        self.poolbot = poolbot

    def match_request(self, text):
        """Return a boolean to determine if this handler should process the message."""
        return NotImplemented()

    def process_request(self, message):
        """Determine an action to take based on the message details."""
        return NotImplemented()

    def reply(self, message, callbacks=None):
        """Return a message to the channel and call further commands via callbacks."""
        if callbacks is None:
            callbacks = []
        return (message, callbacks)

    def _generate_url(self, **kwargs):
        """Join the host portion of the URL with the provided command path."""
        path = self.url_path.format(**kwargs)
        return self.poolbot.generate_url(path)
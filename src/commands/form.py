from .base import BaseCommand


class FormCommand(BaseCommand):
    """Returns the match results of a mentioned user - for example `W W L W`."""

    command_term = 'form'
    url_path = 'api/player/{user_id}/form/'
    help_message = (
        'Use the `form` command to get the recent results for a given user. '
        'For example, `@poolbot form @danny` will return a string like `W W L`. '
        'If no user is passed, grab the message authors stats. By default only '
        'the last ten games are displayed. To fetch more pass an extra argument '
        'like `@poolbot form @danny 20`.'
    )
    DEFAULT_LIMIT = 10

    def process_request(self, message):
        """Get the recent match results for the user mentioned in the text."""
        try:
            user_id = self._find_user_mentions(message['text'])[0]
        except IndexError:
            user_id = message['user']

        # we pass an additional GET limit param to reduce the number of results
        args = self._command_args(message)
        limit = self.DEFAULT_LIMIT
        if args:
            try:
                limit = int(args[0])
            except ValueError:
                pass

        player_form_url = self._generate_url(user_id=user_id)
        response = self.poolbot.session.get(
            player_form_url,
            params={'limit': limit}
        )

        if response.status_code == 200:
            return self.reply(
                'Recent results for {user_name}: `{results}`'.format(
                    user_name=self.poolbot.users[user_id]['name'],
                    results=response.content
                )
            )
        else:
            return self.reply('Unable to get form data')

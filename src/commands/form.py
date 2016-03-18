import requests

from .base import BaseCommand


class FormCommand(BaseCommand):
    """Returns the match results of a mentioned user - for example `W W L W`."""

    command_term = 'form'
    url_path = 'api/player/{user_id}/form/'
    help = (
        'Use the `form` command to get the recent results for a given user.\n'
        'For example, `@poolbot form @danny` will return a string like `W W L`.'
    )

    def process_request(self, message):
        """Get the recent match results for the user mentioned in the text."""
        try:
            user_id = self._find_user_mentions(message)[0]
        except IndexError:
            return 'Sorry, I was unable to find a user in that message...' 

        player_form_url = self._generate_url(user_id=user_id)
        response = requests.get(player_form_url)

        if response.status_code == 200:
            return 'Recent results for {user_name}: `{results}`'.format(
                user_name=self.poolbot.users[user_id]['name'],
                results=response.content
            )
        else:
            return 'Unable to get form data'

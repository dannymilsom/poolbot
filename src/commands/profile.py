from datetime import datetime

from utils import format_datetime_to_date
from .base import BaseCommand


class ProfileCommand(BaseCommand):
    """View your profile and update metadata."""

    command_term = 'profile'
    url_path = 'api/player/{user_id}'
    help_message = (
        'To view your own profile information, type `@poolbot profile`. To '
        'set profile values, use the syntax `@poolbot profile set <fieldname> '
        '<value>`.'
    )

    def process_request(self, message):
        args = self._command_args(message)
        user_id = message['user']
        url = self._generate_url(user_id=user_id)

        if not args:
            # fetch the profile data of the message author from cache/API
            try:
                profile_attrs = self.poolbot.get_player_profile(user_id)
                return self._get_profile_representation(profile_attrs)
            except KeyError:
                response = self.poolbot.session.get(url)
                if response.status_code == 200:
                    profile_attrs = response.json()
                    self.poolbot.set_player_profile(user_id, profile_attrs)
                    return self._get_profile_representation(profile_attrs)

        if args[0] == 'set':
            # trying to update some property on the user profile
            response = self.poolbot.session.patch(
                url,
                data={
                    args[1]: args[2]
                }
            )
            if response.status_code == 200:
                profile_attrs = response.json()
                self.poolbot.set_player_profile(user_id, profile_attrs)
                return self._get_profile_representation(profile_attrs, update=True)

        return 'Sorry, I was unable to fetch that data.'

    def _get_profile_representation(self, profile_data, update=False):
        """Parse the profile data to remove fields we don't want to expose,
        and format the response so it is nice for humans to read."""
        # we don't want to expose the slack_id
        del profile_data['slack_id']

        # and we want a human friendly version of the joined timestamp
        profile_data['joined'] = format_datetime_to_date(profile_data['joined'])

        msg = " \n".join(
            '{attribute}: {value}'.format(
                attribute=attribute.title(),
                value=value
            ) for attribute, value in profile_data.items()
        )

        prefix = (
            "Update was successful! New profile data: \n" if
            update else
            "Profile data: \n"
        )

        return "{prefix}{body}".format(prefix=prefix, body=msg)

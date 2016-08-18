from .base import BaseCommand


class ChallengeCommand(BaseCommand):
    """Initiates a match, where the initiating player is looking for an
    opponent to play. Subsuequently other players can accept the game.
    """

    command_term = 'challenge'
    url_path = 'api/challenge/'
    help_message = (
        'Invoke a challenge to other players in the room with `@poolbot '
        'challenge`. Accept an existing challenge with `@poolbot challenge '
        'accept`.'
    )


    def setup(self):
        """Each channel poolbot is in requires a unique challenge instance.
        To avoid the overhead when processing messages, POST to create the
        missing ones when poolbot loads."""
        response = self.poolbot.session.get(self._generate_url())
        if response.status_code == 200:
            challenge_channels = set(
                [challenge['channel'] for challenge in response.json()]
            )

        all_poolbot_channels = set(self.poolbot.poolbot_channels)
        missing_channels = all_poolbot_channels.difference(challenge_channels)

        for channel_id in missing_channels:
            response = self.poolbot.session.post(
                self._generate_url(),
                data={
                    'channel': channel_id,
                }
            )

    def process_request(self, message):
        """The two main commands to interpret are:
            * @poolbot: challenge - which invokes a new challenge
            * @poolbot: challenge accept - which accepts an existing challenge
        """
        author = message['user']
        command_args = self._command_args(message)
        channel_challenge = self._get_channel_challenge(message['channel'])

        # create a invoke a new challenge
        if not command_args:

            # try and set the initiator to the message author
            response = self.poolbot.session.patch(
                self._get_detail_url(channel_challenge['id']),
                data={
                    'initiator': author
                }
            )

            if response.status_code == 200:
                return self.reply(
                    'New challenge created by {initiator}! Who wants to play?'
                    .format(
                        initiator=self.poolbot.get_username(author)
                    )
                )
            else:
                return self.reply(self._get_validation_error(response))

        # otherwise find the channel challenge instance and update the players
        elif command_args[0] == 'accept':

            # update the related players in the challenge object
            response = self.poolbot.session.patch(
                self._get_detail_url(channel_challenge['id']),
                data={
                    'challenger': author
                }
            )

            if response.status_code == 200:
                data = response.json()
                return self.reply(
                    'To the baize! {initiator} vs {challenger}'.format(
                        initiator=self.poolbot.get_username(data['initiator']),
                        challenger=self.poolbot.get_username(author)
                    )
                )
            else:
                return self.reply(self._get_validation_error(response))
        else:
            return self.reply('Sorry, something went wrong.')

    def _get_channel_challenge(self, channel):
        """Retrives the channel speicifc challenge instance."""
        response = self.poolbot.session.get(
            self._generate_url(),
            params={
                'channel': channel,
            }
        )
        if response.status_code == 200:
            return response.json()[0]

    def _get_detail_url(self, channel_pk):
        """Generate the detail URL of a challenge instance."""
        return "{base_url}{detail_pk}/".format(
            base_url=self._generate_url(),
            detail_pk=str(channel_pk)
        )

    def _get_validation_error(self, response):
        """Returns the validation errors from a request object, falling back
        to the resposne reason if no explicit errors are found."""
        try:
            return response.json()['non_field_errors'][0]
        except KeyError:
            return response.reason

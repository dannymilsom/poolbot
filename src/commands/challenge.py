from .base import BaseCommand


class ChallengeCommand(BaseCommand):
    """Initiates a match, where the initiating player is looking for an
    opponent to play. Subsuequently other players can accept the game.
    """

    command_term = 'challenge'
    url_path = 'api/challenge/'

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
        if len(command_args) == 1:

            # try and set the initiator to the message author
            response = self.poolbot.session.patch(
                "{base_url}{detail_pk}/".format(
                    base_url=self._generate_url(),
                    detail_pk=str(channel_challenge['id'])
                ),
                data={
                    'initiator': author
                }
            )

            # the server will perform some validation to check that
            # this action is permitted, which is true when:
            #   * both initiator and challenger fields are null
            #   * if the initiator and challenger are not null,
            #     but the last modified time is >10mins ago

            if response.status_code == 200:
                return (
                    'New challenge created by {initiator}! Who wants to play?'.format(
                        initiator=self.poolbot.get_username(author)
                    )
                )
            elif response.status_code == 400:
                try:
                    return response.json()['non_field_errors'][0]
                except KeyError:
                    return response.reason

        # otherwise find the channel challenge instance and update the players
        elif command_args[1] == 'accept':

            # update the related players in the challenge object
            response = self.poolbot.session.patch(
                "{base_url}{detail_pk}/".format(
                    base_url=self._generate_url(),
                    detail_pk=str(channel_challenge['id'])
                ),
                data={
                    'challenger': author
                }
            )

            if response.status_code == 200:
                data = response.json()
                return (
                    'To the baize! {initiator} vs {challenger}'.format(
                        initiator=self.poolbot.get_username(data[0]['initiator']),
                        challenger=self.poolbot.get_username(author)
                    )
                )
            else:
                try:
                    return response.json()['non_field_errors'][0]
                except KeyError:
                    return response.reason
        else:
            return 'Sorry, something went wrong.'

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

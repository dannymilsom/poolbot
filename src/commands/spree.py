from .base import BaseCommand


class SpreeCommand(BaseCommand):
    """Returns current player active sprees."""

    command_term = 'spree'
    url_path = 'api/player/{user_id}/form/'
    help_message = (
        'Use the `spree` command to get any current sprees a player it on. '
    )
    DEFAULT_LIMIT = 10

    SPREE_TABLE = {
        2: ('is on a', 'Double Kill', ''),
        3: ('is on a', 'Triple Kill', ''),
        4: ('has commited', 'Overkill', ''),
        5: ('is', 'Killtacular', ''),
        6: ('has commited', 'Killtrocity', ''),
        7: ('is climbing', 'Killamanjaro', ''),
        8: ('has caused a', 'Killtastrophe', ''),
        9: ('has started the', 'Killpocalypse', ''),
        10: ('is a', 'Killionaire', '!!!')
    }

    HIGHEST_SPREE = max(SPREE_TABLE.keys())

    def calculate_spree(self, record):
        record = record[::-1]
        record = record.split()

        spree = 0
        for entry in record:
            entry = entry.replace('"', '')
            if entry == 'W':
                spree += 1
            else:
                break

        # cover cases where the number is higher than the spree table max
        if spree > self.HIGHEST_SPREE:
            spree = self.HIGHEST_SPREE

        spree_msg = self.SPREE_TABLE.get(spree, None)

        return spree_msg, spree

    def process_request(self, message):
        """Get the recent match results for the user mentioned in the text."""
        try:
            user_id = self._find_user_mentions(message)[0]
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
            spree, spree_count = self.calculate_spree(response.content)
            if spree:
                return self.reply(
                    '{username} {prefix} {spree} {suffix} ({count} consecutive wins)'.format(
                        username=self.poolbot.get_username(user_id),
                        prefix=spree[0],
                        spree=spree[1],
                        suffix=spree[2],
                        count=spree_count,
                    )
                )
            else:
                return self.reply('')

        else:
            return self.reply('Unable to get spree data')

from datetime import date

from utils import format_datetime_to_date

from .base import BaseCommand


class EloHistoryCommand(BaseCommand):
    """Returns elo history information!"""

    command_term = 'elo-history'
    url_path = 'api/elo-history/'
    default_elo = 1000
    help_message = (
        'The elo history command returns data about a players elo points over time. '
        'You can explicitly pass a player name, or just type `@poolbot elo-history` '
        'to retrieve your own stats.'
    )
    response_msg = (
        'Elo history for {name}:\n'
        '```\n'
        'Highest points: {highest_elo} on {highest_date}.\n'
        'Lowest points: {lowest_elo} on {lowest_date}.\n'
        'Todays net points: {today_net}.\n'
        'Month net points: {month_net}.\n'
        '```\n'
    )

    def process_request(self, message):
        try:
            user_id = self._find_user_mentions(message['text'])[0]
        except IndexError:
            user_id = message['user']

        url = self._generate_url()
        response = self.poolbot.session.get(
            url,
            params={'player': user_id}
        )
        if response.status_code == 200:
            elo_history_data = response.json()

            high_elo = max(elo_history_data, key=lambda x: x['elo_score'])
            low_elo = min(elo_history_data, key=lambda x: x['elo_score'])

            today_net_elo = self.get_today_net_elo(elo_history_data)
            month_net_elo = self.get_month_net_elo(elo_history_data)

            reply_msg = self.response_msg.format(
                name=self.poolbot.users[user_id],
                highest_elo=high_elo['elo_score'],
                highest_date=format_datetime_to_date(high_elo['date']),
                lowest_elo=low_elo['elo_score'],
                lowest_date=format_datetime_to_date(low_elo['date']),
                today_net=today_net_elo,
                month_net=month_net_elo,
            )
            return self.reply(reply_msg)

        return self.reply("Unable to get elo history data.")

    def get_today_net_elo(self, elo_history_data):
        """Calculate the net points won or loss today for a player."""
        today_date = date.today()

        # first filter by todays date
        today_elos = [
            history['elo_score'] for history in elo_history_data if
            format_datetime_to_date(history['date'], format_date=False) == today_date
        ]

        # if no games today - exit early with 0
        if not today_elos:
            return 0

        # we also need the players last recorded score previous from today
        # if this is not found, or the previous history instance was from
        # a different season, fallback to 1000 elo points
        previous_elo_score = self.default_elo
        date_sorted_elos = sorted(elo_history_data, key=lambda x: x['date'])
        for i, elo_history in enumerate(date_sorted_elos):
            if format_datetime_to_date(elo_history['date'], format_date=False) == today_date:
                try:
                    previous_elo = date_sorted_elos[i-1]
                except IndexError:
                    break # use default
                else:
                    # double check the previous elo is not from a different season!
                    if elo_history['season'] == previous_elo['season']:
                        previous_elo_score = previous_elo['elo_score']
                    break

        all_elo_scores = [previous_elo_score] + today_elos
        today_elo_net = sum([
            all_elo_scores[i+1] - all_elo_scores[i] for
            i in xrange(len(all_elo_scores) -1)
        ])

        # prefix a + sign if positive
        if today_elo_net > 0:
            today_elo_net = "+ {elo_net}".format(elo_net=today_elo_net)

        return today_elo_net

    def get_month_net_elo(self, elo_history_data):
        """Calculate the net points won or loss over current month for a player."""
        current_month = date.today().month

        # filter by current month
        month_elos = [
            history for history in elo_history_data if
            format_datetime_to_date(history['date'], format_date=False).month == current_month
        ]

        # if no games this month exit early
        if not month_elos:
            return 0

        # also make sure all matches are from the current season - otherwise
        # the change in elo points being reset to 1000 distorts everything
        current_season = month_elos[-1]['season']
        month_elos_in_season = [
            history['elo_score'] for history in month_elos if
            history['season'] == current_season
        ]

        # we also need the players last recorded score previous from the month
        # if this is not found, or the previous history instance was from
        # a different season, fallback to 1000 elo points
        previous_elo_score = self.default_elo
        date_sorted_elos = sorted(elo_history_data, key=lambda x: x['date'])
        for i, elo_history in enumerate(date_sorted_elos):
            history_month = format_datetime_to_date(elo_history['date'], format_date=False).month 
            if history_month == current_month and elo_history['season'] == current_season:
                try:
                    previous_elo = date_sorted_elos[i-1]
                except IndexError:
                    break # use the default
                else:
                    # double check the previous elo is not from a different season!
                    if elo_history['season'] == previous_elo['season']:
                        previous_elo_score = previous_elo['elo_score']
                    break

        all_scores = [previous_elo_score] + month_elos_in_season
        month_elo_net = sum([
            all_scores[i+1] - all_scores[i] for
            i in xrange(len(all_scores) -1)
        ])

        # prefix a + sign if positive
        if month_elo_net > 0:
            month_elo_net = "+ {elo_net}".format(elo_net=month_elo_net)

        return month_elo_net
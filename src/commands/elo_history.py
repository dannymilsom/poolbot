from datetime import date

from utils import format_datetime_to_date

from .base import BaseCommand


class EloHistoryCommand(BaseCommand):
    """Returns elo history information!"""

    command_term = 'elo-history'
    url_path = 'api/elo-history/'
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

            # get all time elo high
            high_elo = max(elo_history_data, key=lambda x: x['elo_score'])

            # get all time elo low
            low_elo = min(elo_history_data, key=lambda x: x['elo_score'])

            # get all the elo history instances for today, and work out the net score
            today_elos = [
                history['elo_score'] for history in elo_history_data if
                format_datetime_to_date(history['date'], format_date=False) == date.today()
            ]

            # we also need their last recorded elo not from today
            # so order all elos by date - get the index of the first one recorded today and get -1
            date_sorted_elos = sorted(elo_history_data, key=lambda x: x['date'])
            for i, elo_history in enumerate(date_sorted_elos):
                if format_datetime_to_date(elo_history['date'], format_date=False) == date.today():
                    previous_elo = date_sorted_elos[i-1]['elo_score']

            all_scores = [previous_elo] + today_elos

            today_elo_net = sum([
                all_scores[i+1] - all_scores[i] for
                i in xrange(len(all_scores) -1)
            ])

            # prefix a + sign if positive
            if today_elo_net:
                today_elo_net = "+ {elo_net}".format(elo_net=today_elo_net)

            # get all elo history instances for the month, and workout the net score
            month_elos = [
                history['elo_score'] for history in elo_history_data if
                format_datetime_to_date(history['date'], format_date=False).month == date.today().month
            ]

            # we also need their last recorded elo not from today
            # so order all elos by date - get the index of the first one recorded today and get -1
            date_sorted_elos = sorted(elo_history_data, key=lambda x: x['date'])
            for i, elo_history in enumerate(date_sorted_elos):
                if format_datetime_to_date(elo_history['date'], format_date=False).month == date.today().month:
                    previous_elo = date_sorted_elos[i-1]['elo_score']

            all_scores = [previous_elo] + month_elos

            month_elo_net = sum([
                all_scores[i+1] - all_scores[i] for
                i in xrange(len(all_scores) -1)
            ])
            # prefix a + sign if positive
            if month_elo_net:
                month_elo_net = "+ {elo_net}".format(elo_net=month_elo_net)

            reply_msg = self.response_msg.format(
                name=self.poolbot.users[user_id],
                highest_elo=high_elo['elo_score'],
                highest_date=format_datetime_to_date(high_elo['date']),
                lowest_elo=low_elo['elo_score'],
                lowest_date=format_datetime_to_date(low_elo['date']),
                today_net=today_elo_net,
                month_net=month_elo_net,
            )

            return self.reply(reply_msg)

        return self.reply("Unable to get elo history data.")
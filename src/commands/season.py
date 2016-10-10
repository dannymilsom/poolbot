from datetime import datetime

from utils import format_datetime_to_date
from .base import BaseCommand


class SeasonCommand(BaseCommand):
    """Information about each season."""

    command_term = 'seasons'
    url_path = 'api/season/'
    reply_template = "{name}: {start_date} until {end_date}"
    default_reply = "Sorry, I was unable to get the season data!"
    help_message = (
        "To view a season in more detail, use the syntax `@poolbot <seasonname>`."
    )

    def process_request(self, message):
        args = self._command_args(message)
        if args:
            # join all the args into a space seperated string
            season_name = ' '.join(arg for arg in args)
            response_txt = self.season_detail(season_name)
        else:
            response_txt = self.season_list()
        return (
            self.reply(response_txt) if
            response_txt else
            self.reply(self.default_reply)
        )

    def season_list(self):
        """Find all season instances and return them in a formatted list"""
        season_url = self._generate_url()
        get_params = {'ordering': 'end_date'}
        response = self.poolbot.session.get(season_url, params=get_params)

        if response.status_code == 200:
            return self.format_season_response(response.json())

    def season_detail(self, season_name):
        """Find all season player instances and format into a leaderboard."""
        season_url = self._generate_url()
        response = self.poolbot.session.get(season_url)

        if response.status_code == 200:
            season = self.find_season(season_name, response.json())
            if season is None:
                return (
                    "Unable to get data for the season {season}. "
                    "Are you sure there is a season with this name?".format(
                        season=season_name
                    )
                )
            else:
                season_player_url = self.poolbot.generate_url('api/season-player/')
                get_params = {'season': season['pk']}
                response = self.poolbot.session.get(
                    season_player_url,
                    params=get_params
                )

                if response.status_code == 200:
                    return self.format_season_player_responses(season, response.json())

    def find_season(self, season_name, season_data):
        for season in season_data:
            if season['name'] == season_name:
                return season

    def format_season_response(self, data):
        """Format the season list response."""
        return "\n".join(
            self.reply_template.format(**season) for season in data
        )

    def format_season_player_responses(self, season, season_player_data):
        """Format the season players into a ordered leaderboard."""
        leading_text = 'Leaderboard for {season} ({start} to {end})'.format(
            season=season['name'],
            start=season['start_date'],
            end=season['end_date']
        )

        leaderboard_row_msg = '{ranking}. {name} [Elo Score: {elo}] ({wins} W / {losses} L)'
        leaderboard_table_rows = []

        for player in season_player_data:
            if player['match_count']:
                leaderboard_table_rows.append(leaderboard_row_msg.format(
                    ranking=len(leaderboard_table_rows) + 1,
                    name=self.poolbot.users[player['player']],
                    wins=player['win_count'],
                    losses=player['loss_count'],
                    elo=player['elo_score'])
                )
        table_output = ' \n'.join(leaderboard_table_rows)

        return '{prefix} \n ```\n{table}```\n'.format(
            prefix=leading_text,
            table=table_output
        )
import random

from utils import get_ordinal_extension

from .base import BaseCommand


class RecordCommand(BaseCommand):
    """Records the result of a match between two players."""

    command_term = 'record'
    url_path = 'api/match/'
    victory_nouns = (
        'beat',
        'battered',
        'defeated',
        'destroyed',
        'crushed',
        'clobbered',
        'crushed',
        'defeated',
        'disgraced',
        'emasculated',
        'grilled',
        'embarrassed',
        'humiliated',
        'grannied',
        'hammered',
        'obliterated',
        'pounded',
        'trounced',
        'thrashed',
        'slayed',
        'smashed',
        'spangled',
        'walloped',
    )
    briefmode_flags = (
        '-brief',
        '-mini',
        '-short'
    )
    help_message = (
        'Record the outcome of a game between two players with the command '
        '`@poolbot record beat <opponent>`.'
    )
    no_user_found_message = (
        'Sorry, I was unable to find an opponent in that message...'
    )
    cannot_beat_yourself_message = (
        'Sorry, but you cannot record a victory against yourself.'
    )
    no_victory_noun_found_message = (
        'Sorry, I am unable to determine the result. Record a win by posting'
        'a message like `record beat @opponent`. You can replace `beat` with '
        'any word from the following list:\n `{victory_nouns}`'
    )
    not_recorded_message = (
        'Sorry, I was unable to record that result.'
    )
    victory_message = (
        'Victory recorded for {winner}! :{emoji}: {winner} gained '
        '{delta_elo_winner} elo points, giving a new total of {winner_total}. '
        '{winner} has {position_winner} place in the leaderboard now ({winner_emoji} '
        '{delta_position_winner}). {loser} lost {delta_elo_loser} points, giving '
        'them a new total of {loser_total}. {loser} has {position_loser} place '
        'in the leaderboard now ({loser_emoji} {delta_position_loser}).'
    )
    victory_message_brief = (
        '{winner} [#{old_position_winner} | {old_elo_winner}] > {loser} [#{old_position_loser} | {old_elo_loser}]'
        '{winner} + {delta_elo_winner} = [#{position_winner} | {winner_total}]'
        '{loser} + {delta_elo_loser} = [#{position_loser} | {loser_total}]'
    )

    def process_request(self, message):
        """The message author is the winner and the mentioned user the loser."""
        msg_author = message['user']

        # detect the defeated player, ensuring a user does not beat themself
        defeated_player = self._find_defeated_player(message['text'])
        if defeated_player is None:
            return self.reply(self.no_user_found_message)
        elif defeated_player == msg_author:
            return self.reply(self.cannot_beat_yourself)

        # make sure the author is recording a win
        lower_text = message['text'].lower()
        if not self._victory_noun_in_text(lower_text):
            victory_nouns = ', '.join(noun for noun in self.victory_nouns)
            return self.reply(
                self.no_victory_noun_found_message.format(
                    victory_nouns=victory_nouns
                )
            )

        # check if brief message mode is enabled
        brief = self._find_briefmode_flag(message['text'].lower())

        # cache the elo score of each player before recording the win
        original_elo_winner = self._get_elo(msg_author)
        original_elo_loser = self._get_elo(defeated_player)

        # cache the leaderboard position of each player before recording the win
        original_position_winner = self.poolbot.get_leaderboard_position(msg_author)
        original_position_loser = self.poolbot.get_leaderboard_position(defeated_player)

        response = self.poolbot.session.post(
            self._generate_url(),
            data={
                'winner': msg_author,
                'loser': defeated_player,
                'channel': message['channel'],
                'granny': 'grannied' in lower_text,
            }
        )

        if response.status_code == 201:

            # also check if we need to update an active challenge, so
            # fetch the challenge instance for the room
            # response = self.poolbot.session.get(
            #     self.poolbot.generate_url('api/challenge'),
            #     params={
            #         'channel': message['channel'],
            #     }
            # )
            # if response.status_code == 200:
            #     # see if the two players match
            #     data = response.json()
            #     if len(data):
            #         challenge_players = (
            #             data[0]['initiator'],
            #             data[0]['challenger']
            #         )
            #         if msg_author in challenge_players and defeated_player in challenge_players:
            #             # bingo - update the players now the result is recorded
            #             challenge_pk = data[0]['id']
            #             response = self.poolbot.session.patch(
            #                 self.poolbot.generate_url(
            #                     'api/challenge/{challenge_pk}/'.format(
            #                         challenge_pk=challenge_pk
            #                     )
            #                 ),
            #                 data={
            #                     'initiator': '',
            #                     'challenger': ''
            #                 }
            #             )

            # fetch the new elo score after the match has been recorded
            # and store it in the player profile cache
            updated_elo_winner = self._get_elo(msg_author, from_cache=False)
            updated_elo_loser = self._get_elo(defeated_player, from_cache=False)

            # fetch the new leaderboard position after the match has been recorded
            updated_position_winner = self.poolbot.get_leaderboard_position(msg_author)
            updated_position_loser = self.poolbot.get_leaderboard_position(defeated_player)

            delta_elo_winner = updated_elo_winner - original_elo_winner
            delta_elo_loser = abs(updated_elo_loser - original_elo_loser)
            delta_position_winner = abs(updated_position_winner - original_position_winner)
            delta_position_loser = updated_position_loser - original_position_loser

            message = self.victory_message_brief if brief == True else self.victory_message

            return self.reply(
                message.format(
                    winner=self.poolbot.get_username(msg_author),
                    loser=self.poolbot.get_username(defeated_player),
                    delta_elo_winner=delta_elo_winner,
                    delta_elo_loser=delta_elo_loser,
                    winner_total=updated_elo_winner,
                    loser_total=updated_elo_loser,
                    emoji=self._get_emojis(),
                    delta_position_winner=delta_position_winner,
                    delta_position_loser=delta_position_loser,
                    position_winner=get_ordinal_extension(updated_position_winner),
                    position_loser=get_ordinal_extension(updated_position_loser),
                    winner_emoji=self._get_position_change_emoji(delta_position_winner),
                    loser_emoji=self._get_position_change_emoji(-delta_position_loser),
                    old_elo_winner=original_elo_winner,
                    old_elo_loser=original_elo_loser,
                    old_position_winner=original_position_winner,
                    old_position_loser=original_position_loser
                ),
                callbacks=['spree']
            )
        else:
            return self.reply(self.not_recorded_message)
        # TODO generate some funny phrase to celebrate the victory
        # eg highlight an unbetean run, or X consequtive lose etc

    def _find_defeated_player(self, text):
        """Look for a user mention in the message text."""
        try:
            return self._find_user_mentions(text)[0]
        except IndexError:
            return None

    def _find_briefmode_flag(self, text):
        """
        Search for a brief flag in the message text.
        """
        return any(noun in text for noun in self.briefmode_flags)

    def _victory_noun_in_text(self, text):
        """
        Search for a victory noun in the message text. To support more elaborate
        text, the position of the noun in the text is not checked.
        """
        return any(noun in text for noun in self.victory_nouns)

    def _get_elo(self, player, from_cache=True):
        """Find a players elo points, via the cache or API. If we send a request
        to the API, store the latest profile in the cache as a side effect.
        """
        if from_cache:
            try:
                player_profile = self.poolbot.get_player_profile(player)
            except KeyError:
                pass # we fallback to fetching via the API
            else:
                return player_profile['elo']

        # if fetching from cache was un-successful / not intended, hit the API
        base_url = '/api/player/{player}/'.format(player=player)
        response = self.poolbot.session.get(
            self.poolbot.generate_url(base_url)
        )
        if response.status_code == 200:
            data = response.json()
            elo = int(data['elo'])

            # we also use this opportunity to update the cached player profle
            self.poolbot.set_player_profile(player, data)
        else:
            elo = 0

        return elo

    def _get_position_change_emoji(self, position_change):
        """Return a emoji to represent a users movement on the leaderboard."""
        if position_change == 0:
            emoji = 'left_right_arrow'
        elif position_change > 0:
            emoji = 'arrow_up'
        elif position_change < 0:
            emoji = 'arrow_down'
        return ':{emoji}:'.format(emoji=emoji)

    def _get_emojis(self):
        """Returns a random emojis to append to the victory reply."""
        emojis = self.poolbot.config['record_emojis']
        return random.choice(emojis)

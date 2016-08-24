import unittest
import os

import mock

from commands import RecordCommand
from tests.data.poolbot_api import player
from .base import BaseCommandTestCase


class RecordCommandTestCase(BaseCommandTestCase):
    """Tests for the RecordCommand class."""

    def setUp(self):
        """Initalize the RecordCommand - it is needed by all the tests."""
        super(RecordCommandTestCase, self).setUp()
        self.record_cmd = RecordCommand(poolbot=self.poolbot)

    def test_match_handler(self):
        """Assert that the command correctly matches the term."""
        # assert correct text is processed as relevant
        text = '{term} beat <@USERID>'.format(term=self.record_cmd.command_term)
        self.assertTrue(self.record_cmd.match_request(text))

        # assert a leading whitespace is stripped
        text = ' {term} beat <@USERID>'.format(term=self.record_cmd.command_term)
        self.assertTrue(self.record_cmd.match_request(text))

    def test_victory_nouns_in_text(self):
        """
        Assert that the command accurately checks the message text to
        ensure a victory noun is included.
        """
        self.record_cmd = RecordCommand(poolbot=self.poolbot)

        # assert message text with any victory nouns return True
        for vic_noun in self.record_cmd.victory_nouns:
            text = '{term} {noun} <@USERID>'.format(
                term=self.record_cmd.command_term,
                noun=vic_noun,
            )
            self.assertTrue(self.record_cmd._victory_noun_in_text(text))

        # assert a missing victory noun returns False
        text = '{term} {noun} <@USERID>'.format(
            term=self.record_cmd.command_term,
            noun='lost',
        )
        self.assertFalse(self.record_cmd._victory_noun_in_text(text))

    def test_defeated_player_detection(self):
        """
        Assert that the command accurately detects player mentions in the
        message text.
        """
        self.record_cmd = RecordCommand(poolbot=self.poolbot)

        # assert the user ID is found
        text = '{term} beat {user}'.format(
            term=self.record_cmd.command_term,
            user='<@USERID>'
        )
        value = self.record_cmd._find_defeated_player(text)
        self.assertEqual(value, 'USERID')

        # assert no user ID is found
        text = '{term} beat toby'.format(term=self.record_cmd.command_term)
        value = self.record_cmd._find_defeated_player(text)
        self.assertIsNone(value)

        # assert no user mention at all
        text = '{term} beat'.format(term=self.record_cmd.command_term)
        value = self.record_cmd._find_defeated_player(text)
        self.assertIsNone(value)

    def test_post_data(self):
        """
        Assert that when the correct syntax is followed, the victory message
        is returned to the slack channel.
        """
        self.record_cmd = RecordCommand(poolbot=self.poolbot)

        # record a win by the author
        message = {
            "type": "message",
            "channel": "C2147483705",
            "user": player.PLAYER_1['slack_id'],
            "text": "{term} beat <@{user_id}>".format(
                term=self.record_cmd.command_term,
                user_id=player.PLAYER_2['slack_id'],
            ),
            "ts": "1355517523.000005"
        }

        # result should be the victory command message
        reply, callbacks = self.record_cmd.process_request(message)
        self.assertEqual(
            reply,
            self.record_cmd.victory_message.format(
                winner=self.poolbot.get_username(player.PLAYER_1['slack_id']),
                loser=self.poolbot.get_username(player.PLAYER_2['slack_id']),
                delta_elo_winner=0,
                delta_elo_loser=0,
                winner_total=player.PLAYER_1['elo'],
                loser_total=player.PLAYER_2['elo'],
                emoji=self.record_cmd._get_emojis(),
                position_winner=1,
                position_loser=2,
                delta_position_winner=0,
                delta_position_loser=0,
            ),
        )

        # the recording off a win should lead to the spree command being called
        self.assertItemsEqual(callbacks, ['spree'])

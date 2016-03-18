from base import BaseReaction


class ChannelLeaveReaction(BaseReaction):

    def match_request(self, message):
        return message.get('subtype') == 'channel_leave'

    def process_request(self, message):
        return 'Gonna miss you! The blaze is never greener on the other side!'

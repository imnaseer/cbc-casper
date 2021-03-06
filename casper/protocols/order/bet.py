"""The Bet module implements the message data structure for order consensus"""
from casper.message import Message


class Bet(Message):
    """Message data structure for order consensus"""

    @classmethod
    def is_valid_estimate(cls, estimate):
        return isinstance(estimate, list)

    def conflicts_with(self, message):
        """Returns true if the other_message estimate is not the same as this estimate"""
        assert isinstance(message.estimate, list)

        return self.estimate != message.estimate

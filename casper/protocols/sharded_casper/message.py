"""The block module implements the message data structure for a blockchain"""
from casper.message import Message
from casper.protocols.sharded_casper.sharded_casper_constants import Constants

class ShardChains(Message):
    """Message data structure for sharded blockchain consensus"""

    def __init__(self, estimate, justification, sender, sequence_number, display_height):
        super().__init__(estimate, justification, sender, sequence_number, display_height)

    @classmethod
    def is_valid_estimate(cls, estimate):
        if (not isinstance(estimate, dict)):
            return False

        for sid in range(1, Constants.NumberOfShards + 1):
            if (not sid in estimate):
                return False

        if (len(estimate) != Constants.NumberOfShards):
            return False

        for sid in range(1, Constants.NumberOfShards + 1):
            block = estimate[sid]
            if (block.get_shard_id() != sid):
                return False

        return True

    def conflicts_with(self, message):
        """Returns true if self is not in the prev blocks of other_message"""
        assert isinstance(message, ShardChains), "...expected ShardChains"

        my_estimate = self.estimate
        other_estimate = message.estimate

        for sid in range(1, Constants.NumberOfShards + 1):
            if (not is_in_blockchain(my_estimate[sid], other_estimate[sid])):
                return True

        return False

    @staticmethod
    def is_in_blockchain(self, this_block, other_block):
        """Returns True if this_block is an ancestor of other_block."""
        assert isinstance(this_block, Block), "... expected a block"
        assert isinstance(other_block, Block), "...expected a block"

        if this_block == other_block:
            return True

        if other_block.get_parent() is None:
            return False

        return is_in_blockchain(this_block, other_block.get_parent())

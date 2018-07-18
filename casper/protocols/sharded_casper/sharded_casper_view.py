
"""The sharded casper view module extends a view for sharded casper data structures """
from casper.abstract_view import AbstractView
from random import randint
from casper.protocols.sharded_casper.sharded_casper_constants import Constants
from casper.protocols.sharded_casper.block import Block
import casper.protocols.sharded_casper.forkchoice as forkchoice

class ShardedCasperView(AbstractView):
    """A view class that also keeps track of a last_finalized_block and children"""
    def __init__(self, messages=None):
        self.shard_to_children = { sid: dict() for sid in range(1, Constants.NumberOfShards + 1) }
        self.shard_to_last_finalized_block = { sid: Constants.ShardToGenesisBlock[sid] for sid in range(1, Constants.NumberOfShards + 1) }
        self.shard_to_genesis_block = { sid: Constants.ShardToGenesisBlock[sid] for sid in range(1, Constants.NumberOfShards + 1) }

        super().__init__(messages)

    def estimate(self, data=None):
        """Returns the current forkchoice in this view"""
        
        sharded_tips = { sid: forkchoice.get_fork_choice(
            sid,
            self.shard_to_last_finalized_block[sid],
            self.shard_to_children[sid],
            self.latest_messages) for sid in range(1, Constants.NumberOfShards + 1) }

        shard_to_extend = randint(1, Constants.NumberOfShards)
        new_block = Block(shard_to_extend, sharded_tips[shard_to_extend], [], [])
        sharded_tips[shard_to_extend] = new_block

        return sharded_tips

    def update_safe_estimates(self, validator_set):
        pass

    def _update_protocol_specific_view(self, message):
        """Given a now justified message, updates children and when_recieved"""
        assert message.hash in self.justified_messages, "...should not have seen message!"

        for sid in message.estimate:
            tip = message.estimate[sid]
            parent = tip.get_parent()

            children = self.shard_to_children[sid]

            if parent not in children:
                children[parent] = set()

            children[parent].add(tip)

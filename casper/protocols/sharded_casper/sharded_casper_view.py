
"""The sharded casper view module extends a view for sharded casper data structures """
from casper.abstract_view import AbstractView
from random import randint
import random
from casper.protocols.sharded_casper.sharded_casper_constants import Constants, BlockConstants
from casper.protocols.sharded_casper.block import Block, ShardMessage
from casper.utils import get_random_str
import casper.protocols.sharded_casper.forkchoice as forkchoice

class ShardedCasperView(AbstractView):
    """A view class that also keeps track of a last_finalized_block and children"""
    def __init__(self, messages=None):
        self.shard_to_children = { sid: dict() for sid in range(1, Constants.NumberOfShards + 1) }
        self.shard_to_last_finalized_block = { sid: BlockConstants.ShardToGenesisBlock[sid] for sid in range(1, Constants.NumberOfShards + 1) }
        self.shard_to_genesis_block = { sid: BlockConstants.ShardToGenesisBlock[sid] for sid in range(1, Constants.NumberOfShards + 1) }

        super().__init__(messages)

    def estimate(self, data=None):
        """Returns the current forkchoice in this view"""

        sharded_tips = { sid: forkchoice.get_fork_choice(
            sid,
            self.shard_to_last_finalized_block,
            self.shard_to_children,
            self.latest_messages) for sid in range(1, Constants.NumberOfShards + 1) }

            
        sid = randint(1, Constants.NumberOfShards)
        block = sharded_tips[sid]

        sent_messages = [item for sublist in block.sent_map.values() for item in sublist]
        new_sent_map = { sid: [sm for sm in block.sent_map[sid]] for sid in range(1, Constants.NumberOfShards + 1) }

        if ((len(sent_messages) < Constants.PerShardSendLimit) and
            random.Random().random() < 0.3):

            target_sid = 1 if sid == 2 else 2
            new_sm = ShardMessage("x-shard-" + get_random_str(6), sharded_tips[target_sid], 1000)
            new_sent_map[target_sid].append(new_sm)

        received_messages = [item for sublist in block.received_map.values() for item in sublist]
        new_received_map = { sid: [sm for sm in block.received_map[sid]] for sid in range(1, Constants.NumberOfShards + 1) }
        
        if ((len(received_messages) < Constants.PerShardReceiveLimit) and
            random.Random().random() < 0.5):

            source_sid = 1 if sid == 2 else 2

            # We don't have to check for duplicate receives as
            # PerShardReceiveLimit is one, if it was greater than one
            # then we'll have to make sure we don't receive the same
            # message twice

            sent_list = sharded_tips[source_sid].sent_map[sid]
            if (len(sent_list) == 1):
                new_rm = ShardMessage(sent_list[0].msg, sent_list[0].base_block, sent_list[0].time_to_live)
                new_received_map[source_sid].append(new_rm)
        
        new_block = Block(
            sid,
            sharded_tips[sid],
            new_sent_map,
            new_received_map)
        sharded_tips[sid] = new_block

        self._print_new_messages(sid, block, new_block)

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

    def _print_new_messages(self, sid, block, new_block):

        print_separator = False
        
        for target_sid in range(1, Constants.NumberOfShards + 1):
            if sid == target_sid:
                continue

            sent_list = block.sent_map[target_sid]
            new_sent_list = new_block.sent_map[target_sid]
            sent_diff_len = len(new_sent_list) - len(sent_list)
            
            if (sent_diff_len > 0):
                print("Newly sent messages from {} to {}".format(sid, target_sid))
                print(new_sent_list[-sent_diff_len:])
                print()

                print_separator = True

        for source_sid in range(1, Constants.NumberOfShards + 1):
            if (sid == source_sid):
                continue

            received_list = block.received_map[source_sid]
            new_received_list = new_block.received_map[source_sid]
            received_diff_len = len(new_received_list) - len(received_list)

            if (received_diff_len > 0):
                print("Newly received messages from {} to {}".format(source_sid, sid))
                print(new_received_list[-received_diff_len:])
                print()

                print_separator = True

        if (print_separator):
            print("~~")

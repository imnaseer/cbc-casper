"""The block module implements the block data structure for a blockchain"""
from casper.message import Message

# parent block, data, sent queue, received queue
# sent queue: [i x base block x N]*
# received queue: [i x base block x N]*

class ShardMessage:
    def __init__(self, shard_id, base_block, time_to_live):
        self.shard_id = shard_id
        self.base_block = base_block
        self.time_to_live = time_to_live


class Block:
    """Block data structure for blockchain consensus"""
       
    NameCounter = 0

    def __init__(self, shard_id, parent, sent_queue, received_queue, name=None):

        # number of blocks since genesis
        if parent:
            self.height = parent.height + 1
        else:
            self.height = 1

        if name:
            self.name = name
        else:
            Block.NameCounter = Block.NameCounter + 1
            self.name = "B" + str(Block.NameCounter)

        self.parent = parent
        self.shard_id = shard_id
        self.sent_queue = sent_queue
        self.received_queue = received_queue

    def get_name(self):
        return self.name

    def get_shard_id(self):
        return self.shard_id

    def get_parent(self):
        return self.parent

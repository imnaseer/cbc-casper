"""The block module implements the block data structure for a blockchain"""
from casper.message import Message

class ShardMessage:
    def __init__(self, msg, base_block, time_to_live):
        self.msg = msg
        self.base_block = base_block
        self.time_to_live = time_to_live

    def __repr__(self):
        return "shard-msg({}, {}, {})".format(self.msg, self.base_block.name, self.time_to_live)

class Block:
    """Block data structure for blockchain consensus"""
       
    NameCounter = 0

    def __init__(self, shard_id, parent, sent_map, received_map, name=None):

        # number of blocks since genesis
        if parent:
            self.height = parent.height + 1
        else:
            self.height = 1

        self.parent = parent
        self.shard_id = shard_id
        self.sent_map = sent_map
        self.received_map = received_map

        if name:
            self.name = name
        else:
            Block.NameCounter = Block.NameCounter + 1
            self.name = "B" + str(Block.NameCounter) + "_" + str(self.shard_id)

    def get_name(self):
        return self.name

    def get_shard_id(self):
        return self.shard_id

    def get_parent(self):
        return self.parent


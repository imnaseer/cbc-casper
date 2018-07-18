
from casper.protocols.sharded_casper.block import Block

class Constants:
    NumberOfShards = 2

    ShardToGenesisBlock = { sid: Block(sid, None, [], [], "G" + str(sid)) for sid in range(1, NumberOfShards + 1) }

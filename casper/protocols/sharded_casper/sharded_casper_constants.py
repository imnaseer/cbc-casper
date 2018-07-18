
from casper.protocols.sharded_casper.block import Block

class Constants:
    NumberOfShards = 2

class BlockConstants:

    ShardToGenesisBlock = {
        sid: Block(
            sid,
            None,
            { sid2: [] for sid2 in range(1, Constants.NumberOfShards + 1) },
            { sid2: [] for sid2 in range(1, Constants.NumberOfShards + 1) },
            "G" + str(sid))
        for sid in range(1, Constants.NumberOfShards + 1)
    }

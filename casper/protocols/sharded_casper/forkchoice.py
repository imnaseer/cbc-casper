"""The forkchoice module implements the estimator function a blockchain"""

from casper.protocols.sharded_casper.sharded_casper_constants import Constants, BlockConstants

def get_max_weight_indexes(scores):
    """Returns the keys that map to the max value in a dict.
    The max value must be greater than zero."""

    max_score = max(scores.values())

    assert max_score != 0, "max_score of a block should never be zero"

    max_weight_estimates = {e for e in scores if scores[e] == max_score}

    return max_weight_estimates


def ghost_fork_choice(sid, last_finalized_block, children, latest_messages):
    """Returns the estimate by selecting highest weight sub-trees.
    Starts from the last_finalized_block and stops when it reaches a tip."""

    scores = dict()

    for validator in latest_messages:
        current_block = latest_messages[validator].estimate[sid]

        while current_block and current_block != last_finalized_block:
            scores[current_block] = scores.get(current_block, 0) + validator.weight
            current_block = current_block.get_parent()

    best_block = last_finalized_block
    while best_block in children:
        curr_scores = dict()
        max_score = 0
        for child in children[best_block]:
            curr_scores[child] = scores.get(child, 0)
            max_score = max(curr_scores[child], max_score)

        # We don't choose weight 0 children.
        # Also possible to make non-deterministic decision here.
        if max_score == 0:
            break

        max_weight_children = get_max_weight_indexes(curr_scores)

        assert len(max_weight_children) == 1, "... there should be no ties!"

        best_block = max_weight_children.pop()

    return best_block

def get_parent_fork_choice(sid, last_finalized_block, children, latest_messages):
    return ghost_fork_choice(sid, last_finalized_block, children, latest_messages)

def get_child_fork_choice(parent_sid, sid, shard_to_last_finalized_block, shard_to_children, latest_messages):
    #parent_tip = get_parent_fork_choice(parent_sid, shard_to_last_finalized_block[parent_sid], shard_to_children[parent_sid], latest_messages)

    return ghost_fork_choice(sid, shard_to_last_finalized_block[sid], shard_to_children[sid], latest_messages)

def get_fork_choice(sid, shard_to_last_finalized_block, shard_to_children, latest_messages):
    parent_sid = BlockConstants.get_parent_of_shard(sid)
    
    if (parent_sid == None):
        return get_parent_fork_choice(sid, shard_to_last_finalized_block[sid], shard_to_children[sid], latest_messages)
    else:
        return get_child_fork_choice(parent_sid, sid, shard_to_last_finalized_block, shard_to_children, latest_messages)


def has_symmetric_messages(block_s1, block_s2):
    if (not _are_sent_and_received_messages_equal(block_s1, block_s2)):
        return False

    if (not _are_sent_and_received_messages_equal(block_s2, block_s1)):
        return False
    
    return True

def _are_sent_and_received_messages_equal(block_s1, block_s2):
    s1_sent_list = [item for sublist in block_s1.sent_map.values() for item in sublist]
    s1_sent_set = set([item.msg for item in s1_sent_list])
    
    s2_received_list = [item for sublist in block_s2.received_map.values() for item in sublist]
    s2_received_set = set([item.msg for item in s2_received_list])

    return s1_sent_set == s2_received_set


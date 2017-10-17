"""The simulution utils module ... """
import random as r

from casper.validator_set import ValidatorSet


def generate_random_validator_set(
        num_validators=5,
        mu=60,
        sigma=40,
        min_weight=20,
    ):
    """Generates a random validator set."""

    # Give the validators random weights in 0.,BIGINT;
    # this "big" integer's job is to guarantee the "tie-breaking property"
    # that no two subsets of validator's total weights are exactly equal.
    # In prod, we will add a random epsilon to weights given by bond amounts,
    # however, for the purposes of the current work, this will suffice.
    BIGINT = 1000000000000

    names = set(range(num_validators))
    weights = {
        i: max(min_weight, r.gauss(mu, sigma))
           + 1.0/(BIGINT + r.uniform(0, 1)) + r.random()
        for i in names
    }

    return ValidatorSet(weights)
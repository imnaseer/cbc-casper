"""The validator module contains the Validator class, which creates/sends/recieves messages """
import numbers


class Validator(object):
    """A validator has a view from which it generates new messages and detects finalized blocks."""
    def __init__(self, name, weight, validator_set, view_cls, message_cls):
        if name is None:
            raise ValueError("Validator name must be defined.")
        if not isinstance(weight, numbers.Number):
            raise ValueError("Validator weight must a number.")
        if weight < 0:
            raise ValueError("Validator weight cannot be less than 0.")

        self.name = name
        self.weight = weight
        self.validator_set = validator_set

        self.message_class = message_cls
        self.view_class = view_cls
        self.view = None

    def get_name(self):
        return "V" + str(self.name) + "  (" + str(round(self.weight, 1)) + ")"

    def __eq__(self, val):
        if val is None:
            return False
        if not isinstance(val, Validator):
            return False
        return hash(self) == hash(val)

    def __hash__(self):
        # defined differently than self.hash to avoid confusion with builtin
        # use of __hash__ in dictionaries, sets, etc
        return hash(self.name)

    def initialize_view(self, initial_messages):
        self.view = self.view_class(initial_messages)

    def receive_messages(self, messages):
        """Allows the validator to receive protocol messages."""
        self.view.add_messages(messages)

    def estimate(self, data=None):
        """The estimator function returns the set of max weight estimates.
        This may not be a single-element set because the validator may have an empty view."""
        return self.view.estimate(data)

    def my_latest_message(self):
        """This function returns the validator's latest message."""
        if self in self.view.latest_messages:
            return self.view.latest_messages[self]
        return None

    def update_safe_estimates(self):
        """The validator checks estimate safety on some estimate with some safety oracle."""
        self.view.update_safe_estimates(self.validator_set)

    def make_new_message(self, data):
        """This function produces a new latest message for the validator.
        It updates the validator's latest message, estimate, view, and latest observed messages."""
        new_message = self.message_class(
            self.estimate(data),
            self.justification(),
            self,
            self._next_sequence_number(),
            self._next_display_height()
        )
        self.view.add_messages(set([new_message]))
        assert new_message.hash in self.view.justified_messages  # sanity check

        return new_message

    def justification(self):
        """Returns the headers of latest message seen from other validators."""
        latest_message_headers = dict()
        for validator in self.view.latest_messages:
            latest_message_headers[validator] = self.view.latest_messages[validator].hash
        return latest_message_headers

    def _next_sequence_number(self):
        """Returns the sequence number for the next message from a validator"""
        last_message = self.my_latest_message()

        if last_message:
            return last_message.sequence_number + 1
        return 0

    def _next_display_height(self):
        """Returns the display height for a message created in this view"""
        if not any(self.view.latest_messages):
            return 0

        max_height = max(
            self.view.latest_messages[validator].display_height
            for validator in self.view.latest_messages
        )
        return max_height + 1

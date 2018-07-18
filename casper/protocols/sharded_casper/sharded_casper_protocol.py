import json

from casper.utils import get_random_str
from casper.protocol import Protocol
from casper.protocols.sharded_casper.sharded_casper_view import ShardedCasperView
from casper.protocols.sharded_casper.block import Block
from casper.protocols.sharded_casper.message import ShardChains
from casper.protocols.sharded_casper.sharded_casper_plot_tool import ShardedCasperPlotTool
from casper.protocols.sharded_casper.sharded_casper_constants import Constants

class ShardedCasperProtocol(Protocol):
    """A protocol for coming to consensus on sharded casper chains"""
    Message = Block
    View = ShardedCasperView
    PlotTool = ShardedCasperPlotTool

    def __init__(self, json_string, display, save, report_interval):
        parsed_json = self.parse_json(json_string)

        super().__init__(
            parsed_json['config']['validators'],
            parsed_json['execution']['execution_string'],
            parsed_json['execution']['msg_per_round'] * report_interval,
            display,
            save,
            ShardedCasperPlotTool,
            ShardedCasperView,
            ShardChains
        )

        self.set_initial_messages()

        self.plot_tool.plot()

    @staticmethod
    def parse_json(json_string):
        parsed_json = json.loads(json_string)

        assert parsed_json['protocol'] == 'sharded_casper'

        return parsed_json


    def set_initial_messages(self):

        initial_message = ShardChains(
            { sid: Constants.ShardToGenesisBlock[sid] for sid in range(1,Constants.NumberOfShards + 1) },
            dict(),
            self.global_validator_set.get_validator_by_name(0),
            -1,
            0)
        
        self.register_message(initial_message, get_random_str(10))

        for validator in self.global_validator_set:
            validator.initialize_view([initial_message])


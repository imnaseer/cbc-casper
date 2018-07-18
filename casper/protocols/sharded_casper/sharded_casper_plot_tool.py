"""The sharded casper plot tool implements functions for plotting sharded chains
"""
from casper.plot_tool import PlotTool
from casper.protocols.sharded_casper.sharded_casper_constants import Constants

class ShardedCasperPlotTool(PlotTool):
    """The module contains functions for plotting a sharded chain data structure"""

    def __init__(self, display, save, view, validator_set):
        self.save = save
        self.display = display
        self.view = view
        self.round = 0

    def update(self, new_messages=None):
        return

    @staticmethod
    def blockchain_to_string(block):
        str = block.get_name()

        while (block.get_parent() != None):
            str += ' -> ' + block.get_parent().get_name()
            block = block.get_parent()

        return str

    def plot(self):
        print("Round " + str(self.round))
        print("")
        
        for validator in self.view.latest_messages:
            print(validator.get_name())
            for sid in range(1, Constants.NumberOfShards + 1):
                print("  {}: {}".format(sid, ShardedCasperPlotTool.blockchain_to_string(self.view.latest_messages[validator].estimate[sid])))
            print()

        print()
        print("---")
        self.round += 1

        

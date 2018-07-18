"""The sharded casper plot tool implements functions for plotting sharded chains
"""
import matplotlib as mpl
import networkx as nx
mpl.use('TkAgg')
import matplotlib.pyplot as plt  # noqa


from casper.plot_tool import PlotTool
from casper.protocols.sharded_casper.sharded_casper_constants import Constants
import casper.utils as utils

class ShardedCasperPlotTool(PlotTool):
    """The module contains functions for plotting a sharded chain data structure"""

    def __init__(self, display, save, view, validator_set):
        self.save = save
        self.display = display
        self.view = view
        self.validator_set = validator_set
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

        for sid in range(1, Constants.NumberOfShards + 1):
            print("Shard", sid)
            for validator in self.view.latest_messages:
                formatted_name = validator.get_name()
                formatted_name = ' ' * (12 - len(formatted_name)) + formatted_name
                print(formatted_name, ':',
                      ShardedCasperPlotTool.blockchain_to_string(self.view.latest_messages[validator].estimate[sid]))
            print()

        print()
        print("---")
        self.round += 1


    def plot_visual(self):

        fig_size = plt.rcParams["figure.figsize"]
        fig_size[0] = 20
        fig_size[1] = 20
        plt.rcParams["figure.figsize"] = fig_size

        graph = nx.Graph()

        blocks = set()
        edges = set()
        positions = dict()
        labels = dict()
        for sid in range(1, Constants.NumberOfShards + 1):
            for validator in self.view.latest_messages:
                N = len(self.validator_set)
                block = self.view.latest_messages[validator].estimate[sid]
                parent = None
                while block != None:
                    blocks.add(block)
                    positions[block] = (
                        ((sid - 1) * 2 * N + validator.name + 1) / (2.0 * Constants.NumberOfShards * N),
                        0.2 + 0.1 * block.height
                    )
                    labels[block] = block.get_name()
                    if parent != None:
                        edges.add((block, parent))
                    parent = block
                    block = block.get_parent()

        graph.add_nodes_from(blocks)
        graph.add_edges_from(edges)


        #for sid in range(1, Constants.NumberOfShards + 1):
        #    for validator in self.view.latest_messages:
        #        graph.add_edges_from([(self.view.latest_messages[validator],
        #                               self.view.latest_messages[validator].estimate[sid])])

        # positions = dict()
        #
        # sorted_validators = self.validator_set.sorted_by_name()
        # for message in nodes:
        #     # Index of val in list may have some small performance concerns.
        #     if message.estimate is not None:
        #         xslot = sorted_validators.index(message.sender) + 1
        #     else:
        #         xslot = (len(self.validator_set) + 1) / 2.0
        #
        #     positions[message] = (
        #         (float)(xslot) / (float)(len(self.validator_set) + 1),
        #         0.2 + 0.1 * message.display_height
        #     )


        nx.draw_networkx_nodes(graph, positions, alpha=0.5, node_shape='s', node_color='blue', edge_color='black')
        nx.draw_networkx_edges(
            graph,
            positions,
            width=3,
            edge_color='red',
            style='dotted',
            alpha=0.5
        )
        nx.draw_networkx_labels(graph, positions, labels=labels)
        ax = plt.gca()
        # ax.collections[0].set_edgecolor("black")
        #ax.text(0.4, 0.4, "Weights: ", fontsize=20)
        plt.axvline(x=0.5)
        plt.show()

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

    def plot_text(self):
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


    # def add_block_recursively(self, block):
    #     if block in self.blocks:
    #         return
    #     parent = None
    #     while block != None:
    #         blocks.add(block)
    #         positions[block] = (
    #             ((sid - 1) * 2 * N + validator.name + 1) / (2.0 * Constants.NumberOfShards * N),
    #             0.2 + 0.1 * block.height
    #         )
    #         labels[block] = block.get_name()
    #         if parent != None:
    #             parent_edges.add((block, parent))
    #         for sent_map_sid in block.sent_map:
    #             for message in block.sent_map[sent_map_sid]:
    #                 sent_edges.add((message.source_block, message.target_base_block))
    #         for received_map_sid in block.received_map:
    #             for message in block.sent_map[received_map_sid]:
    #                 received_edges.add((message.source_block, message.target_base_block))
    #         parent = block
    #         block = block.get_parent()

    def plot(self):

        fig_size = plt.rcParams["figure.figsize"]
        fig_size[0] = 20
        fig_size[1] = 20
        plt.rcParams["figure.figsize"] = fig_size

        graph = nx.Graph()

        blocks = set()
        parent_edges = set()
        sent_edges = set()
        received_edges = set()
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
                        parent_edges.add((block, parent))
                    for sent_map_sid in block.sent_map:
                        for message in block.sent_map[sent_map_sid]:
                            sent_edges.add((message.source_block, message.target_base_block))
                    for received_map_sid in block.received_map:
                        for message in block.sent_map[received_map_sid]:
                            received_edges.add((message.source_block, block))
                    parent = block
                    block = block.get_parent()

        print(len(sent_edges), len(received_edges))
        filtered_sent_edges = set()
        for edge in sent_edges:
            if edge[0] in blocks and edge[1] in blocks:
                filtered_sent_edges.add(edge)
        sent_edges = filtered_sent_edges
        filtered_received_edges = set()
        for edge in received_edges:
            if edge[0] in blocks and edge[1] in blocks:
                filtered_received_edges.add(edge)
        received_edges = filtered_received_edges
        print(len(sent_edges), len(received_edges))

        graph.add_nodes_from(blocks)

        nx.draw_networkx_nodes(graph, positions, alpha=0.3, node_size=800,
                               node_shape='s', node_color='blue', edge_color='black')

        nx.draw_networkx_edges(
            graph,
            positions,
            edgelist=parent_edges,
            width=3,
            edge_color='blue',
            style='solid',
            alpha=0.5
        )
        nx.draw_networkx_edges(
            graph,
            positions,
            edgelist=sent_edges,
            width=1,
            edge_color='red',
            style='dotted',
            alpha=0.3
        )
        nx.draw_networkx_edges(
            graph,
            positions,
            edgelist=received_edges,
            width=3,
            edge_color='red',
            style='dotted',
            alpha=0.3
        )
        nx.draw_networkx_labels(graph, positions, labels=labels)
        ax = plt.gca()
        # ax.collections[0].set_edgecolor("black")
        #ax.text(0.4, 0.4, "Weights: ", fontsize=20)
        plt.axvline(x=0.42)
        plt.show()

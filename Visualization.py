import matplotlib.colors as colors
import matplotlib.cm as cmx
from numpy import interp

from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import NetworkModule
from mesa.visualization.ModularVisualization import ModularServer

from Model import *
from Posts import *


def get_node_color(agent):
    belief = agent.beliefs[Topic.VAX]
    # Map belief value to color value
    # with PiYG, a diverging colormap:
    #       100 --> green
    #       50 --> white
    #       0 --> red
    c_norm = colors.Normalize(vmin=0, vmax=100)  # because belief can be any value in [0,100]
    scalar_map = cmx.ScalarMappable(norm=c_norm, cmap=plt.get_cmap('PiYG'))

    c_val = scalar_map.to_rgba(belief)
    new_c_val = []
    for idx, val in enumerate(c_val):
        if idx != 3:  # only adjust RGB, not transparency
            new_c_val.append(val * 256)
    c_val = tuple(new_c_val)
    return c_val


def get_edge_width(weight=1, weight_borders=(0, 100)):
    """
    Returns how wide the edge should be displayed.
    :param weight:          float, edge weight
    :param weight_borders:  tuple, (min, max)
    :return:                float, width/thickness of the depicted edge
    """
    min_weight, max_weight = weight_borders
    weight_range = [min_weight, max_weight]
    width_range = [0.1, 2]

    width = interp(weight, weight_range, width_range)
    print(f"width: {width}")  # works

    return width


def show_visualization(model):
    def network_portrayal(G):
        # The model ensures there is always 1 agent per node

        # def get_agents(source, target):
        #     return grid.nodes[source]['agent'][0], grid.nodes[target]['agent'][0]

        portrayal = dict()
        portrayal['nodes'] = [{"shape": "circle",
                               "color": f'rgb{get_node_color(agent)}',
                               "size": 5,
                               "tooltip": f"belief: {round(agent.beliefs[Topic.VAX])}",
                               }
                              for (id, agent) in G.nodes.data("agent")]

        portrayal['edges'] = [{'source': source,
                               'target': target,
                               'color': 'black',
                               'width': 1,
                               # to adjust line-width based on edge-weight, use instead:
                               # 'width': get_edge_width(G.edges[source, target, key]['weight']),
                               'directed': True
                               # 'directed' should work, but doesn't change anything:
                               # https://github.com/projectmesa/mesa/issues/667
                               }
                              for (source, target, key) in G.edges]

        return portrayal

    network = NetworkModule(network_portrayal, 500, 500, library='d3')
    chart = ChartModule([{"Label": "Avg Vax-Belief", "Color": "blue"},
                         {"Label": "Above Vax-Threshold (>=50.0)", "Color": "green"},
                         {"Label": "Below Vax-Threshold (<50.0)", "Color": "red"}],
                        data_collector_name="data_collector")

    server = ModularServer(model,  # class name
                           [network, chart],
                           'Misinfo Model',  # title
                           {'n_agents': 100})  # model parameters

    server.port = 8521  # The default
    server.launch()

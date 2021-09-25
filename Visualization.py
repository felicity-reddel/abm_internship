import sys
import math
import matplotlib.colors as colors
import matplotlib.cm as cmx
import matplotlib.pyplot as plt

from mesa.visualization.ModularVisualization import ModularServer
from mesa.visualization.UserParam import UserSettableParameter
from mesa.visualization.modules import ChartModule
from mesa.visualization.modules import NetworkModule
from mesa.visualization.modules import TextElement

# from .model_network import HostNetwork
# from .model_state import State, number_infected, number_susceptible, number_resistant, number_death

from mesa.visualization.modules import CanvasGrid, NetworkVisualization
from mesa.visualization.ModularVisualization import ModularServer
from Agents import *
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
        if idx != 3:        # only adjust RGB, not transparency
            new_c_val.append(val*256)
    c_val = tuple(new_c_val)
    print(f'c_val: {c_val}')
    return c_val


def show_visualization(model):

    def network_portrayal(G):
        # The model ensures there is always 1 agent per node

        # def get_agents(source, target):
        #     return grid.nodes[source]['agent'][0], grid.nodes[target]['agent'][0]

        portrayal = dict()
        portrayal['nodes'] = [{"shape": "circle",
                               "color": f'rgba({get_node_color(agent)[0]},{get_node_color(agent)[1]},{get_node_color(agent)[2]},1.0)',
                               "size": 5,
                               "tooltip": f"id: {id}",
                               }
                              for (id, agent) in G.nodes.data("agent")]

        portrayal['edges'] = [{'source': source,
                               'target': target,
                               'color': 'black',
                               'width': 1
                               }
                              for (source, target) in G.edges]

        return portrayal

    network = NetworkModule(network_portrayal, 500, 500, library='d3')

    server = ModularServer(model,  # class name
                           [network],  # grid
                           'Misinfo Model',  # title
                           {'n_agents': 10})  # model parameters

    server.port = 8521  # The default
    server.launch()

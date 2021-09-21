import sys
import math

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


def show_visualization(model):

    def network_portrayal(G):
        # The model ensures there is always 1 agent per node

        # def get_agents(source, target):
        #     return network.nodes[source]['agent'][0], network.nodes[target]['agent'][0]

        portrayal = dict()
        portrayal['nodes'] = [{'Shape': "circle",
                               'color': "blue",
                               "size": 5,
                               'tooltip': f"id: {node}"  # ,
                               # 'label': node  # self-added attempt --> no error, no label.
                               # TODO: only uses G, cannot use network instead?
                               }
                              for node in G.nodes]

        portrayal['edges'] = [{'source': source,
                               'target': target,
                               'color': 'black',
                               'width': 1
                               }
                              for (source, target) in G.edges]

        return portrayal

    network = NetworkModule(network_portrayal, 500, 500, library='d3')

    server = ModularServer(model,               # class name
                           [network],           # network
                           'Misinfo Model',     # title
                           {'n_agents': 10})    # model parameters

    server.port = 8521  # The default
    server.launch()

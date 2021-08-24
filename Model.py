from mesa import Model
from mesa.time import RandomActivation
from mesa.space import NetworkGrid
from Agents import *
import networkx as nx
import matplotlib.pyplot as plt


class MisinfoModel(Model):
    """Simple model with n agents."""

    def __init__(self, n_agents, n_edges=3):
        self.num_agents = n_agents
        self.schedule = RandomActivation(self)
        self.G = self.random_graph(n_nodes=n_agents, m=n_edges) # n_nodes = n_agents, exactly 1 agent per node
        self.network = NetworkGrid(self.G)
        # TODO: What need G for what other than drawing graph?
        #       If mesa can visualize network nicely, maybe don't need G as a model-attribute anymore.

        # Create agents
        for i in range(self.num_agents):
            a = BaseAgent(i, self)
            self.schedule.add(a)

        # Place each agent in its node
        for node in self.G.nodes:
            agent = self.schedule.agents[node]
            self.network.place_agent(agent, node)


    def step(self):
        """Advance the model by one step."""
        self.schedule.step()

    ########################################################################################################################
    #                                                 Helper Functions                                                     #
    ########################################################################################################################

    # TODO: Should these two functions be within the MisinfoModel-class or outside of it?
    # --> potentially adjust for toy & random: G = self.toy_graph() to G = toy_graph()
    def toy_graph(self):
        """ Generate and return simple toy-graph of 4 nodes."""
        # Simple graph to test compatibility
        G = nx.Graph()
        G.add_nodes_from([0, 1, 2, 3])
        G.add_edges_from([(0, 1), (0, 2), (0, 3)])
        print(f"G's nodes: \n {str(G[0])}, \n {str(G[1])}, \n {str(G[2])}, \n {str(G[3])}")
        return G

    def random_graph(self, n_nodes, m, seed = None):
        """ Generate and return a random graph via networkx.

        Keyword arguments:
        n -- number of nodes
        m -- number of edges added per node

        Return:
        G -- stochastic graph (barabasi albert graph)

        # TODO: Potential extension: parameter for skew of node degree.
        # Note: Using Barabasi Albert graphs, because they are fitting for social networks.
        #       ( https://en.wikipedia.org/wiki/Barab%C3%A1si%E2%80%93Albert_model )
        # FYI: n=10, m=3, doesn't create 30 edges, but only e.g., 21. Not each node has 3 edges.
        """
        G = nx.barabasi_albert_graph(n_nodes, m, seed)
        return G



def draw_graph(G):
    """ Draw graph G with specified options."""
    size = 4
    options = {
        'node_color': 'lightgray',
        'node_size': 100 * size,
        'width': 3,
        'edge_color': 'black',
        'edgecolors': 'black',
        'font_size': 10
    }

    nx.draw(G, with_labels=True, font_weight='bold', **options)
    plt.show()

from mesa import Model
from mesa.datacollection import DataCollector
from mesa.time import StagedActivation
from mesa.space import NetworkGrid
from Agents import *
from Posts import *
import networkx as nx
import matplotlib.pyplot as plt



class MisinfoModel(Model):
    """Simple model with n agents."""

    def __init__(self, n_agents, n_edges=2):
        super().__init__()
        self.n_agents = n_agents
        self.schedule = StagedActivation(self, stage_list=["share_post_stage", "update_beliefs_stage"])
        self.G = random_graph(n_nodes=n_agents, m=n_edges)  # n_nodes = n_agents, exactly 1 agent per node
        self.grid = NetworkGrid(self.G)
        self.post_id_counter = 0


        # Create agents
        for i in range(self.n_agents):
            a = BaseAgent(i, self)
            self.schedule.add(a)

        # Place each agent in its node. (& save node_position into agent)
        for node in self.G.nodes:  # each node is just an integer (i.e., a node_id)
            agent = self.schedule.agents[node]

            # save node_position into agent
            self.grid.place_agent(agent, node)

            # add agent to node
            self.G.nodes[node]['agent'] = agent

        # Init neighbors (after all agents have been set up)
        for agent in self.schedule.agents:
            agent.neighbors = agent.get_neighbors()

        self.datacollector = DataCollector(model_reporters={
            "Avg Vax-Belief": self.get_avg_VAX_belief,
            # "Belief Category Sizes": self.get_VAX_category_sizes})
            "Above Vax-Threshold (>=50.0)": self.get_above_VAX_threshold,
            "Below Vax-Threshold (<50.0)": self.get_below_VAX_threshold})

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
        self.datacollector.collect(self)


    def get_avg_VAX_belief(self, weird_error_fix_parameter) -> float:  # if without dummy parameter: get error
        """
        Return average belief of all agents on a given topic. For the DataCollector.
        :return:        float
        """
        topic = Topic.VAX

        agent_beliefs = [a.beliefs[topic] for a in self.schedule.agents]
        avg_belief = sum(agent_beliefs) / len(agent_beliefs)

        return avg_belief

    def get_VAX_category_sizes(self, weird_error_fix_parameter) -> tuple:
        """
        Return tuple of how many agents' belief on a given topic is above and below the provided threshold.
         For the DataCollector.
        :param threshold:   float
        :param topic:       Topic
        :return:            tuple
        """
        topic = Topic.VAX
        threshold = 50.0

        agent_beliefs = [a.beliefs[topic] for a in self.schedule.agents]
        n_above = sum([1 for a_belief in agent_beliefs if a_belief >= threshold])
        n_below = len(agent_beliefs) - n_above

        return n_above, n_below

    def get_above_VAX_threshold(self, weird_error_fix_parameter) -> tuple:
        """
        Return tuple of how many agents' belief on a given topic is above and below the provided threshold.
         For the DataCollector.
        :param threshold:   float
        :param topic:       Topic
        :return:            tuple
        """
        topic = Topic.VAX
        threshold = 50.0

        agent_beliefs = [a.beliefs[topic] for a in self.schedule.agents]
        n_above = sum([1 for a_belief in agent_beliefs if a_belief >= threshold])

        return n_above

    def get_below_VAX_threshold(self, weird_error_fix_parameter) -> tuple:
        """
        Return tuple of how many agents' belief on a given topic is above and below the provided threshold.
         For the DataCollector.
        :param threshold:   float
        :param topic:       Topic
        :return:            tuple
        """
        topic = Topic.VAX
        threshold = 50.0

        agent_beliefs = [a.beliefs[topic] for a in self.schedule.agents]
        n_below = sum([1 for a_belief in agent_beliefs if a_belief < threshold])

        return n_below


# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
#   Graph Functions
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

def toy_graph() -> nx.Graph:
    """ Generates and returns simple toy-G of 4 nodes."""
    # Simple G to test compatibility
    graph = nx.Graph()  # Later: potentially adjust in style to later code. i.e., self.G
    graph.add_nodes_from([0, 1, 2, 3])
    graph.add_edges_from([(0, 1), (0, 2), (0, 3)])
    print(f"G's nodes: \n {str(graph[0])}, \n {str(graph[1])}, \n {str(graph[2])}, \n {str(graph[3])}")
    return graph


def random_graph(n_nodes, m, seed=None, directed=True) -> nx.Graph:
    """ Generate and return a random G via networkx.

    Keyword arguments:
    n -- number of nodes
    m -- number of edges added per node

    Return:
    G -- stochastic G (barabasi albert G)

    # Later: Potential extension: parameter for skew of node degree.
    # Note: Using Barabasi Albert graphs, because they are fitting for social networks.
    #       ( https://en.wikipedia.org/wiki/Barab%C3%A1si%E2%80%93Albert_model )
    # FYI: n=10, m=3, doesn't create 30 edges, but only e.g., 21. Not each node has 3 edges.
    """
    graph = nx.barabasi_albert_graph(n_nodes, m, seed)
    # Make graph directed (i.e., asymmetric edges possible)
    if directed:
        graph = nx.DiGraph(graph)  # shallow copy, because don't need two separate graphs
    return graph


def draw_graph(graph):
    """ Draw G G with specified options."""
    size = 4
    options = {
        'node_color': 'lightgray',
        'node_size': 100 * size,
        'width': 3,
        'edge_color': 'black',
        'edgecolors': 'black',
        'font_size': 10
    }

    nx.draw(graph, with_labels=True, font_weight='bold', **options)
    plt.show()

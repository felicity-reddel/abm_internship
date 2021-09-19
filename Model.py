import random

from mesa import Model
from mesa.time import RandomActivation
from mesa.space import NetworkGrid
from Agents import *
from Posts import *
import networkx as nx
import matplotlib.pyplot as plt


class MisinfoModel(Model):
    """Simple model with n agents."""

    def __init__(self, n_agents, n_edges=3, n_posts=10):
        super().__init__()
        self.num_agents = n_agents
        self.schedule = RandomActivation(self)
        self.graph = random_graph(n_nodes=n_agents, m=n_edges)  # n_nodes = n_agents, exactly 1 agent per node
        self.network = NetworkGrid(self.graph)
        # Later: What need graph for what other than drawing graph?
        #       If mesa can visualize network nicely, maybe don't need G as a model-attribute anymore.
        self.post_id_counter = 0
        self.posts = self.init_posts(n_posts)

        # Create agents
        for i in range(self.num_agents):
            a = BaseAgent(i, self)
            self.schedule.add(a)

        # Place each agent in its node
        for node in self.graph.nodes:
            agent = self.schedule.agents[node]
            self.network.place_agent(agent, node)

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #   Posts Functions
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    def init_posts(self, n_posts) -> list:
        """
        Initializes the posts.
        :rtype: list
        :param n_posts:
        :return: list of initial posts
        """

        # Generate posts
        posts = []
        for i in range(n_posts):
            messages = sample_messages()
            post = Post(unique_id=i, messages=messages)
            posts += post

        # Update model's post_id_counter
        self.post_id_counter += n_posts

        return posts


def sample_messages(max_n_messages=1) -> dict:
    """
    Generates messages. Each message consists of a topic and the post's stance on it. {Topic.TOPIC1: int}
    :rtype: dict
    :return: dict of messages.
    """
    # Sample how many messages should be included in post. By default 1 message per post.
    n_messages = random.randint(1, max_n_messages)  # Ext: could sample how many messages should be included in post

    # Sample messages
    messages = {}
    for m in range(n_messages):
        topics = [topic for topic in Topic]
        topic = random.choice(topics)  # Ext: could adjust weights for diff. topics
        stance = random.randint(0, 100)
        messages[topic] = stance

    return messages

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #   Graph Functions
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


def toy_graph() -> nx.Graph:
    """ Generates and returns simple toy-graph of 4 nodes."""
    # Simple graph to test compatibility
    graph = nx.Graph()
    graph.add_nodes_from([0, 1, 2, 3])
    graph.add_edges_from([(0, 1), (0, 2), (0, 3)])
    print(f"graph's nodes: \n {str(graph[0])}, \n {str(graph[1])}, \n {str(graph[2])}, \n {str(graph[3])}")
    return graph


def random_graph(n_nodes, m, seed=None) -> nx.Graph:
    """ Generate and return a random graph via networkx.

    Keyword arguments:
    n -- number of nodes
    m -- number of edges added per node

    Return:
    G -- stochastic graph (barabasi albert graph)

    # Later: Potential extension: parameter for skew of node degree.
    # Note: Using Barabasi Albert graphs, because they are fitting for social networks.
    #       ( https://en.wikipedia.org/wiki/Barab%C3%A1si%E2%80%93Albert_model )
    # FYI: n=10, m=3, doesn't create 30 edges, but only e.g., 21. Not each node has 3 edges.
    """
    graph = nx.barabasi_albert_graph(n_nodes, m, seed)
    return graph


def draw_graph(graph):
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

    nx.draw(graph, with_labels=True, font_weight='bold', **options)
    plt.show()

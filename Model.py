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
        self.agents_data = {'n_followers_range': (0, 0),
                            'n_following_range': (0, 0)}
        self.init_agents()
        self.init_followers_and_following()

        self.data_collector = DataCollector(model_reporters={
            "Avg Vax-Belief": self.get_avg_vax_belief,
            # "Belief Category Sizes": self.get_vax_category_sizes})
            # "Above Vax-Threshold (>=50.0)": self.get_above_vax_threshold,
            # "Below Vax-Threshold (<50.0)": self.get_below_vax_threshold,
            "Avg Vax-Belief above threshold": self.get_avg_above_vax_threshold,
            "Avg Vax-Belief below threshold": self.get_avg_below_vax_threshold})

    def step(self):
        """Advance the model by one step."""
        self.schedule.step()
        self.data_collector.collect(self)

    def get_avg_vax_belief(self, dummy) -> float:  # if without dummy parameter: get error
        """
        Return average belief of all agents on a given topic. For the DataCollector.
        :return:        float
        """
        topic = Topic.VAX

        agent_beliefs = [a.beliefs[topic] for a in self.schedule.agents]
        avg_belief = sum(agent_beliefs) / len(agent_beliefs)

        return avg_belief

    def get_vax_category_sizes(self, dummy) -> tuple:
        """
        Return tuple of how many agents' belief on a given topic is above and below the provided threshold.
         For the DataCollector.
        # :param threshold:   float  # to make it more programmatic later
        # :param topic:       Topic  # to make it more programmatic later
        :return:            tuple
        """
        topic = Topic.VAX
        threshold = 50.0

        agent_beliefs = [a.beliefs[topic] for a in self.schedule.agents]
        n_above = sum([1 for a_belief in agent_beliefs if a_belief >= threshold])
        n_below = len(agent_beliefs) - n_above

        return n_above, n_below

    def get_above_vax_threshold(self, dummy) -> int:   # adjust code later: threshold_dict={Topic.VAX: 50.0}?
        """
        Returns how many agents' belief on a given topic is above and below the provided threshold.
         For the DataCollector.
        # :param threshold_dict:   dict {Topic: float}  # to make it more programmatic later. Not sure whether possible.
        :return: int
        """
        topic = Topic.VAX
        threshold = 50.0

        agent_beliefs = [a.beliefs[topic] for a in self.schedule.agents]
        n_above = sum([1 for a_belief in agent_beliefs if a_belief >= threshold])

        return n_above

    def get_below_vax_threshold(self, dummy) -> int:
        """
        Returns how many agents' belief on a given topic is above and below the provided threshold.
         For the DataCollector.
        # :param threshold:   float  # to make it more programmatic later
        # :param topic:       Topic  # to make it more programmatic later
        :return:            tuple
        """
        topic = Topic.VAX
        threshold = 50.0

        agent_beliefs = [a.beliefs[topic] for a in self.schedule.agents]
        n_below = sum([1 for a_belief in agent_beliefs if a_belief < threshold])

        return n_below

    def get_avg_above_vax_threshold(self, dummy) -> float:
        """
        Returns the average belief of agents that are above the provided threshold.
         For the DataCollector.
        :return: float
        """
        topic = Topic.VAX
        threshold = 50.0

        beliefs_above_threshold = [a.beliefs[topic] for a in self.schedule.agents if a.beliefs[topic] >= threshold]
        if len(beliefs_above_threshold) == 0:
            avg = self.get_avg_below_vax_threshold(self)  # If nobody above threshold, take avg of below threshold.
        else:
            avg = sum(beliefs_above_threshold) / len(beliefs_above_threshold)
        return avg

    def get_avg_below_vax_threshold(self, dummy) -> float:
        """
        Returns the average belief of agents that are below the provided threshold.
         For the DataCollector.
        :return: float
        """
        topic = Topic.VAX
        threshold = 50.0

        beliefs_below_threshold = [a.beliefs[topic] for a in self.schedule.agents if a.beliefs[topic] < threshold]

        if len(beliefs_below_threshold) == 0:
            avg = self.get_avg_above_vax_threshold(self)  # If nobody below threshold, take avg of above threshold.
        else:
            avg = sum(beliefs_below_threshold) / len(beliefs_below_threshold)

        return avg

    def init_agents(self):
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

    def init_followers_and_following(self):
        n_followers_list = []
        n_following_list = []

        # Init followers & following (after all agents have been set up)
        for agent in self.schedule.agents:
            # Gather connected agents
            predecessors = [self.schedule.agents[a] for a in self.G.predecessors(agent.unique_id)]
            successors = [self.schedule.agents[a] for a in self.G.successors(agent.unique_id)]

            # Assign to this agent
            agent.following = predecessors
            agent.followers = successors

            # Gather number of followers/following to this agent
            n_following_list.append(len(agent.following))
            n_followers_list.append(len(agent.followers))

            # print(f"agent {agent.unique_id} predecessors: {[agent.unique_id for agent in predecessors]}")
            # print(f"agent {agent.unique_id} successors: {[agent.unique_id for agent in predecessors]}")

        # Gather boundaries of ranges (n_followers & n_following)
        min_n_following = min(n_following_list)
        max_n_following = max(n_following_list)
        min_n_followers = min(n_followers_list)
        max_n_followers = max(n_followers_list)

        # Save ranges into agents_data
        self.agents_data["n_following_range"] = (min_n_following, max_n_following)
        self.agents_data["n_followers_range"] = (min_n_followers, max_n_followers)


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
    """

    :param n_nodes:     int, number of nodes
    :param m:           int, avg number of edges added per node
    :param seed:        int, random seed
    :param directed:    bool, undirected or directed graph

    :return:            nx.Graph, the resulting stochastic graph (barabasi albert G)

    # Note:     Using Barabasi Albert graphs, because they are fitting for social networks.
    #           ( https://en.wikipedia.org/wiki/Barab%C3%A1si%E2%80%93Albert_model )
    # Later:    Potential extension: parameter for skew of node degree.
    # FYI:      n=10, m=3, doesn't create 30 edges, but only e.g., 21. Not each node has 3 edges.
    """
    graph = nx.barabasi_albert_graph(n_nodes, m, seed)
    # print(f'graph edges: {graph.edges}')
    # print(f'len graph edges: {len(graph.edges)}')

    if directed:  # --> has key
        # Make graph directed (i.e., asymmetric edges possible = multiple directed edges)
        graph = nx.MultiDiGraph(graph)  # undirected --> "=bidirectional"

        # Add edge weights
        for edge in graph.edges:
            from_e = edge[0]
            to_e = edge[1]
            key = edge[2]

            # Sample weights & save them
            weight = random.randint(0, 100)
            graph.edges[from_e, to_e, key]['weight'] = weight

    else:  # not directed --> no key
        # Add edge weights
        for edge in graph.edges:
            from_e = edge[0]
            to_e = edge[1]

            # Sample weights & save them
            weight = 1 + random.random() * random.choice([-1, 1])  # weights in range [0,2]: no visible change
            graph.edges[from_e, to_e]['weight'] = weight

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

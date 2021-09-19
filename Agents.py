from mesa import Agent
from Posts import *


class BaseAgent(Agent):
    """Most simple agent to start with."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

        self.beliefs = {}
        self.init_beliefs()
        self.neighbors = self.get_neighbors()  # Need to assign neighbors when all agents are already setup

    def step(self):
        self.toy_interaction()
        # self.adjust_to_average()

        # Testing
        # post = self.create_post(based_on_beliefs=True)

    # Later: More realistic interaction. Adjust way of interaction.
    # Challenge: everyone needs to update. But they should all do so using the *previous* stances of each-other.
    # Such that the order of who updates first is not relevant. How to do that?

    def init_beliefs(self):
        """
        Initialize for each topic a random belief.
        :return:
        """
        for topic in Topic:
            self.beliefs[topic] = self.random.randint(0, 100)

    def create_post(self, based_on_beliefs=True):
        """
        Creates a new post. Either random or based on own stances.
        :return: Post
        """
        # Get post_id & post's stances
        id = self.model.post_id_counter + 1
        if based_on_beliefs:
            stances = Post.sample_stances(based_on_agent=self)
        else:
            stances = Post.sample_stances()

        # Create post
        post = Post(id, stances)

        return post

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #   General Helper-Functions
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    def print_vax_decision(self, threshold=50.0):
        """
        Print the vaccination_willingness value and the corresponding decision.
        :param threshold:   float, decision-threshold for/against getting vaccinated
        """
        # Print value and decision
        decision = "vaccine"
        if self.beliefs[Topic.VAX] <= threshold:
            decision = "NO VACCINE !!1!"

        print("Agent " + str(self.unique_id) + ": " + str(self.beliefs[Topic.VAX])
              + " --> " + decision)

    def get_neighbors(self, node=None):
        """
        Returns all neighbors of a node. If no specific node is provided, the own neighbors are returned.
        :return:    list of agents in neighboring nodes
        """

        # Get neighboring nodes
        if not node:  # If no node provided, get own neighbors.
            neighbor_nodes = self.model.network.get_neighbors(self.unique_id)
        else:
            neighbor_nodes = self.model.network.get_neighbors(node.unique_id)

        # Get agents from neighboring nodes
        neighbor_agents = [self.model.network.get_cell_list_contents([node]) for node in neighbor_nodes]
        neighbor_agents = sum(neighbor_agents, [])  # Flatten the list

        return neighbor_agents

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #   Toy Interaction: 1-on-1, Certainty-based update. Without Posts.
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    def toy_interaction(self):
        """ Toy interaction step method.
        An agent only interacts with one randomly selected neighbor.
        The agent who was less certain updates very strongly towards the more certain agent's belief.
        The agent who was more certain becomes even a bit more certain (due to the strong update of the other agent)."""

        # Pick neighbor
        neighbors = self.get_neighbors()
        other_agent = self.random.choice(neighbors)
        # Determine who is more certain
        more_certain_agent, less_certain_agent = self.toy_get_more_certain_agent(other_agent)
        # Update stances accordingly
        self.toy_update_beliefs(more_certain_agent, less_certain_agent)

    def toy_get_more_certain_agent(self, other_agent):
        """ For toy_interaction. Determine which agent is more/less certain and return them. """
        # Determine which agent was more certain
        # more certain --> further away from middle (i.e., from 50)
        more_certain_agent = other_agent
        less_certain_agent = self
        if abs(self.beliefs[Topic.VAX] - 50) > abs(other_agent.beliefs[Topic.VAX] - 50):
            more_certain_agent = self
            less_certain_agent = other_agent
        return more_certain_agent, less_certain_agent

    @staticmethod
    def toy_update_beliefs(more_certain_agent, less_certain_agent):
        """ For toy_interaction. Determine new belief-values and assign them for both agents.
        :type more_certain_agent: agent object, agent with more extreme belief
        :type less_certain_agent: agent object, agent with less extreme belief
        """
        # Update agents' stances
        # was less certain --> update to average belief of both agents
        less_certain_agent.beliefs[Topic.VAX] = round(
            (more_certain_agent.beliefs[Topic.VAX] + less_certain_agent.beliefs[Topic.VAX]) / 2)
        # was more certain --> become even more certain of belief
        if more_certain_agent.beliefs[Topic.VAX] >= 50:
            more_certain_agent.beliefs[Topic.VAX] = more_certain_agent.beliefs[Topic.VAX] + 1
            # Introduce upper-bound of 100
            # = min(100, more_certain_agent.beliefs[Topic.VAX] + 1)
        else:
            more_certain_agent.beliefs[Topic.VAX] = more_certain_agent.beliefs[Topic.VAX] - 1
            # Introduce lower-bound of 0
            # = max(0, more_certain_agent.beliefs[Topic.VAX] - 1)

    # Lesson from Toy:
    # - Outcome strongly depends on initial conditions, i.e., initial belief distribution (randomly sampled here).
    #   Either all/most agents get the vaccine or all/most don't. Very extreme values.

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #  Toy Interaction: Many-on-1, Average-based update. Without Posts.
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    def adjust_to_average(self):
        # Get neighbors' stances
        self.neighbors = self.get_neighbors()  # to make sure the neighbors are uptodate
        neighbors_beliefs = [neighbor.beliefs[Topic.VAX] for neighbor in self.neighbors]

        # Update own belief towards average neighbor-belief
        avg_neighbor_belief = sum(neighbors_beliefs) / len(neighbors_beliefs)
        self.beliefs[Topic.VAX] = (self.beliefs[Topic.VAX] + avg_neighbor_belief) / 2

    # Lesson from adjust_to_average:
    # - Outcome strongly depends on initial conditions, i.e., initial belief distribution (randomly sampled here).
    #   Either all/most agents get the vaccine or all/most don't. Moderate values.

from mesa import Agent


class BaseAgent(Agent):
    """Most simple agent to start with."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

        # vaccination_willingness: between 0 and 100 [%]
        self.vaccination_willingness = self.random.randint(0, 100)
        self.neighbors = self.get_neighbors()  # Need to assign neighbors when all agents are already setup

    def step(self):
        # self.toy_interaction()
        self.adjust_to_average()

    # Later: More realistic interaction. Adjust way of interaction.
    # Challenge: everyone needs to update. But they should all do so using the *previous* beliefs of each-other.
    # Such that the order of who updates first is not relevant. How to do that?

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #  Interaction: many-on-1, average-based update
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    def adjust_to_average(self):
        # Get neighbors' beliefs
        self.neighbors = self.get_neighbors() # to make sure the neighbors are uptodate
        neighbors_beliefs = [neighbor.vaccination_willingness for neighbor in self.neighbors]

        # Update own belief towards average neighbor-belief
        avg_neighbor_belief = sum(neighbors_beliefs)/len(neighbors_beliefs)
        self.vaccination_willingness = (self.vaccination_willingness + avg_neighbor_belief)/2

    # Lesson from adjust_to_average:
    # - Outcome strongly depends on intial conditions, i.e., initial belief distribution (randomly sampled here).
    #   Either all/most agents get the vaccine or all/most don't. Moderate values.

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #   Toy Interaction: 1-on-1, certainty-based update
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
        # Update beliefs accordingly
        self.toy_update_beliefs(more_certain_agent, less_certain_agent)

    def toy_get_more_certain_agent(self, other_agent):
        """ For toy_interaction. Determine which agent is more/less certain and return them. """
        # Determine which agent was more certain
        # more certain --> further away from middle (i.e., from 50)
        more_certain_agent = other_agent
        less_certain_agent = self
        if abs(self.vaccination_willingness - 50) > abs(other_agent.vaccination_willingness - 50):
            more_certain_agent = self
            less_certain_agent = other_agent
        return more_certain_agent, less_certain_agent

    def toy_update_beliefs(self, more_certain_agent, less_certain_agent):
        """ For toy_interaction. Determine new belief-values and assign them for both agents.
        :type more_certain_agent: agent object, agent with more extreme belief
        :type less_certain_agent: agent object, agent with less extreme belief
        """
        # Update agents' beliefs
        # was less certain --> update to average belief of both agents
        less_certain_agent.vaccination_willingness = round(
            (more_certain_agent.vaccination_willingness + less_certain_agent.vaccination_willingness) / 2)
        # was more certain --> become even more certain of belief
        if more_certain_agent.vaccination_willingness >= 50:
            more_certain_agent.vaccination_willingness = more_certain_agent.vaccination_willingness + 1
            # Introduce upper-bound of 100
            # = min(100, more_certain_agent.vaccination_willingness + 1)
        else:
            more_certain_agent.vaccination_willingness = more_certain_agent.vaccination_willingness - 1
            # Introduce lower-bound of 0
            # = max(0, more_certain_agent.vaccination_willingness - 1)

    # Lesson from Toy:
    # - Outcome strongly depends on intial conditions, i.e., initial belief distribution (randomly sampled here).
    #   Either all/most agents get the vaccine or all/most don't. Very extreme values.
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    def print_vax_decision(self, threshold=50.0):
        """
        Print the vaccination_willingness value and the corresponding decision.
        :param threshold:   float, decision-threshold for/against getting vaccinated
        """
        # Print value and decision
        decision = "vaccine"
        if self.vaccination_willingness <= threshold:
            decision = "NO VACCINE !!1!"

        print("Agent " + str(self.unique_id) + ": " + str(self.vaccination_willingness)
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

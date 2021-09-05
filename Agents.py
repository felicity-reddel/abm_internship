from mesa import Agent


class BaseAgent(Agent):
    """Most simple agent to start with."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

        # vaccination_willingness: between 0 and 100 [%]
        self.vaccination_willingness = self.random.randint(0, 100)

    def step(self):
        self.toy_interaction()

    # Later: More realistic interation. Adjust way of interaction.
    #       Interact with all neighbors – expose them to your memes, update beliefs.

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #   Toy Interaction
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    def toy_interaction(self):
        """ Toy interaction step method.
        An agent only interacts with one randomly selected neighbor.
        The agent who was less certain updates very strongly towards the more certain agent's belief. """

        # Pick neighbor & determine who is more certain
        other_agent = self.toy_pick_neighbor()
        more_certain_agent, less_certain_agent = self.toy_get_more_certain_agent(other_agent)
        # Update beliefs accordingly
        self.toy_update_beliefs(more_certain_agent, less_certain_agent)

    def toy_pick_neighbor(self):
        """ For toy_interaction. Pick random neighbor and return it. """
        # Pick neighbor to interact with
        neighbor_nodes = self.model.network.get_neighbors(self.unique_id)
        other_agents_node = self.random.choice(neighbor_nodes)
        other_agent = self.model.network.get_cell_list_contents([other_agents_node])[
            0]  # [0]: idx of only agent on node
        return other_agent

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
    #   Either all/most agents get the vaccine or all/most don't.
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

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

    # Not sure whether the below fn is needed.
    # def update_belief(self, new_value=50):
    #     """Updates own (vaccination_willingness) belief to provided new value.
    #
    #
    #     Disclaimer: This function should later be replaced with the below extension.
    #                 But currently: doesn't know 'self'.
    #     """
    #     self.vaccination_willingness = new_value

    # EXTENSION: When multiple beliefs
    # def update_belief(self, belief=self.vaccination_willingness, new_value=50):
    #     self.vaccination_willingness = new_value
    #     pass


from mesa import Agent

class BaseAgent(Agent):
    """Most simple agent to start with."""
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

        # vaccination_willingness: between 0 and 100 [%]
        # self.vaccination_willingness = 90
        self.vaccination_willingness = self.random.randint(0, 100)




    def step(self):
        # TODO: adjust way of interaction. Interact with all neighbors – expose them to your memes, update beliefs.
        # Pick neighbor to interact with
        neighbor_nodes = self.model.network.get_neighbors(self.unique_id)
        other_agents_node = self.random.choice(neighbor_nodes)
        other_agent = self.model.network.get_cell_list_contents([other_agents_node])[0] # [0]: idx of only agent on node


        # Determine which agent was more certain
        # more certain --> further away from middle (i.e., from 50)
        more_certain_agent = other_agent
        less_certain_agent = self
        if abs(self.vaccination_willingness - 50) > abs(other_agent.vaccination_willingness - 50):
            more_certain_agent = self
            less_certain_agent = other_agent


        # Update agents' beliefs
        # was less certain --> update to average belief of both agents
        less_certain_agent.vaccination_willingness = round((other_agent.vaccination_willingness + self.vaccination_willingness) / 2)
        # was more certain --> become even more certain of belief
        if more_certain_agent.vaccination_willingness >= 50:
            more_certain_agent.vaccination_willingness = more_certain_agent.vaccination_willingness + 1 #= min(100, more_certain_agent.vaccination_willingness + 1)
        else:
            more_certain_agent.vaccination_willingness = more_certain_agent.vaccination_willingness - 1 #= max(0, more_certain_agent.vaccination_willingness - 1)


        # Print value and decision
        decision = "vaccine"
        if self.vaccination_willingness <= 50:
            decision = "NO VACCINE !!1!"

        print("Agent " + str(self.unique_id) + ": " + str(self.vaccination_willingness)
              + " --> " + decision)

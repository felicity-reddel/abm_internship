
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from Model import MisinfoModel, draw_graph
import matplotlib.pyplot as plt


# setup model
model = MisinfoModel(10)
draw_graph(model.graph)

# run model
for i in range(10):
    model.step()

# plot results
agent_vaccination_willingness = [a.vaccination_willingness for a in model.schedule.agents]
plt.hist(agent_vaccination_willingness)
plt.xlabel("vaccination willingness")
plt.ylabel("number of agents")
plt.show()

# print decisions
for agent in model.schedule.agents:
    agent.print_vax_decision()

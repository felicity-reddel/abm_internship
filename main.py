
# Press Double ⇧ to search everywhere for classes, files, tool windows, actions, and settings.

from Model import MisinfoModel, draw_graph
import matplotlib.pyplot as plt
from Posts import *
from Visualization import *



# setup model
# model = MisinfoModel(10)
# draw_graph(model.G)

# run model
# for i in range(3):
#     model.step()

# # plot results
# agent_vaccination_willingness = [a.beliefs[Topic.VAX] for a in model.schedule.agents]
# plt.hist(agent_vaccination_willingness)
# plt.xlabel("vaccination willingness")
# plt.ylabel("number of agents")
# plt.show()

# print decisions
# for agent in model.schedule.agents:
#     agent.print_vax_decision()

show_visualization(MisinfoModel)  # only needs this line. run model in browser. above model not used. Separate.

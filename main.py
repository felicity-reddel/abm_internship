from Model import MisinfoModel  # , draw_graph
from Visualization import *
import time

visualize = True

if visualize:
    show_visualization(MisinfoModel)  # only needs this line. run model in browser. above model not used. Separate.

else:
    max_run_length = 100
    n_agents = 1000
    n_edges = 10
    media_literacy_intervention = (0.0, SelectAgentsBy.RANDOM)
    ranking_intervention = True

    model = MisinfoModel(n_agents=n_agents,
                         n_edges=n_edges,
                         media_literacy_intervention=media_literacy_intervention,
                         ranking_intervention=ranking_intervention)

    print(f"Starting")
    start_time = time.time()
    for i in range(max_run_length):
        model.step()
        if i % 10 == 0:
            print(f"step {i} done")

    run_time = round(time.time() - start_time, 2)
    print(f"With {max_run_length} steps, runtime is {run_time}")

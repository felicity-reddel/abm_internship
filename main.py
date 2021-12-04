from Model import MisinfoModel  # , draw_graph
from Visualization import *
from Agents import *
import time


if __name__ == '__main__':

    # Parameters
    visualize = True
    n_agents = 100
    agent_ratio = {NormalUser.__name__: 0.9, Disinformer.__name__: 0.1}
    n_edges = 3
    media_literacy_intervention = (0.0, SelectAgentsBy.RANDOM)
    ranking_intervention = False

    if visualize:

        # only needs this line. run model in browser. above model not used. Separate.
        show_visualization(MisinfoModel,
                           n_agents,
                           n_edges,
                           agent_ratio,
                           media_literacy_intervention,
                           ranking_intervention)

    else:

        max_run_length = 1

        model = MisinfoModel(n_agents=n_agents,
                             n_edges=n_edges,
                             agent_ratio=agent_ratio,
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

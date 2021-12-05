import itertools
import os

import pandas as pd
from Model import MisinfoModel  # , draw_graph
from Visualization import *
from Agents import *
import time


def calculate_avg_belief(model):
    topic_name = str(Topic.VAX)
    beliefs = []
    for agent in model.schedule.agents:
        agent_belief_on_topic = agent.beliefs[topic_name]
        beliefs.append(agent_belief_on_topic)

    avg_belief = sum(beliefs) / len(beliefs)

    return avg_belief


def calculate_percentage_agents_above_threshold(model, threshold):
    agent_beliefs = [a.beliefs[str(Topic.VAX)] for a in model.schedule.agents]
    n_above = sum([1 for a_belief in agent_beliefs if a_belief >= threshold])
    percentage_above = n_above / len(model.schedule.agents)
    return percentage_above


if __name__ == '__main__':

    n_agents = 1000
    n_edges = 3
    max_run_length = 60
    n_replications = 50
    kpi_2_threshold = 75

    # Scenarios = different agent_ratios
    scenarios = [{NormalUser.__name__: 1.0, Disinformer.__name__: 0.0},
                 {NormalUser.__name__: 0.95, Disinformer.__name__: 0.05},
                 {NormalUser.__name__: 0.8, Disinformer.__name__: 0.2},
                 {NormalUser.__name__: 0.25, Disinformer.__name__: 0.75}]

    # Policies = combinations of intervention values
    media_literacy_intervention_values = [(0.0, SelectAgentsBy.RANDOM),
                                          (0.1, SelectAgentsBy.RANDOM),
                                          (0.25, SelectAgentsBy.RANDOM),
                                          (0.9, SelectAgentsBy.RANDOM)]
    ranking_intervention_values = [True, False]

    policies = list(itertools.product(media_literacy_intervention_values, ranking_intervention_values))

    for policy in policies:
        print(f'policy: {str(policy)}')

    # Printing
    print(f"Starting")
    start_time = time.time()

    # Run Experiments
    for i, scenario in enumerate(scenarios):  # Each scenario is 1 ratio of agent types
        # Set up data structures
        kpi_1 = pd.DataFrame({"Replication": list(range(0, n_replications))})
        kpi_2 = pd.DataFrame({"Replication": list(range(0, n_replications))})

        for policy in policies:
            # Unpack policy
            media_literacy_intervention, ranking_intervention = policy

            # Set up data structure
            kpi_1_column_data = []
            kpi_2_column_data = []

            for replication in range(n_replications):
                # Set up the model
                model = MisinfoModel(n_agents=n_agents,
                                     n_edges=n_edges,
                                     agent_ratio=scenario,
                                     media_literacy_intervention=media_literacy_intervention,
                                     ranking_intervention=ranking_intervention)

                # Save start data
                # KPI_1
                avg_start_belief = calculate_avg_belief(model)
                # KPI_2
                above_threshold_start = calculate_percentage_agents_above_threshold(model, threshold=kpi_2_threshold)

                # Run the model
                for tick in range(max_run_length):
                    model.step()

                # Save end data (KPI_1 & KPI_2)
                # KPI_1
                # - avg_end_belief (over all agents)
                avg_end_belief = calculate_avg_belief(model)
                # --> avg_update (over all agents) over the whole run
                avg_update = avg_end_belief - avg_start_belief
                # --> add avg_update to list later add to policy-column of scenario-KPI_1-combination
                kpi_1_column_data.append(avg_update)

                # KPI_2
                above_threshold_end = calculate_percentage_agents_above_threshold(model, threshold=kpi_2_threshold)
                # save data from this replication
                replication_data = (above_threshold_start, above_threshold_start)
                kpi_2_column_data.append(replication_data)

            # Create policy columns
            kpi_1_policy_column = pd.Series(kpi_1_column_data, name=str(policy))
            kpi_2_policy_column = pd.Series(kpi_2_column_data, name=str(policy))
            # Save policy column into the dataframe
            kpi_1 = kpi_1.join(kpi_1_policy_column)
            kpi_2 = kpi_2.join(kpi_2_policy_column)

        # Save scenario data into 2 csv files (1 per KPI)
        directory = os.getcwd()
        path = directory + '/results/'

        kpi_1_name = "KPI_1_" + str(scenario) + ".csv"
        kpi_1.to_csv(path + kpi_1_name)

        kpi_2_name = "KPI_2_" + str(scenario) + ".csv"
        kpi_2.to_csv(path + kpi_2_name)

        # Printing
        print(f"scenario {i} done")

    # Printing
    run_time = round(time.time() - start_time, 2)
    print(f"With {max_run_length} steps, runtime is {run_time}")
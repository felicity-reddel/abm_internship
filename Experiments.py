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

    # Scenarios = different agent_ratios
    scenarios = [{NormalUser.__name__: 0.99, Disinformer.__name__: 0.01}]  # ,
    # {NormalUser.__name__: 0.95, Disinformer.__name__: 0.05},
    # {NormalUser.__name__: 0.8, Disinformer.__name__: 0.2},
    # {NormalUser.__name__: 0.25, Disinformer.__name__: 0.75}]

    # Policies = combinations of intervention values
    media_literacy_intervention_values = [(0.0, SelectAgentsBy.RANDOM),
                                          (0.1, SelectAgentsBy.RANDOM),
                                          (0.25, SelectAgentsBy.RANDOM)]  # , (0.9, SelectAgentsBy.RANDOM)]
    ranking_intervention_values = [True, False]

    policies = list(itertools.product(media_literacy_intervention_values, ranking_intervention_values))

    for policy in policies:
        print(f'policy: {str(policy)}')

    # Printing
    start_time_seconds = time.time()
    start_time = time.localtime(time.time())
    human_understandable_time = time.strftime('%Y-%m-%d %H:%M:%S', start_time)
    print(f"\nStarting at time: {human_understandable_time}")

    # Run Experiments
    for i, scenario in enumerate(scenarios):  # Each scenario is 1 ratio of agent types
        # Set up data structures
        data = pd.DataFrame({"Replication": list(range(0, n_replications))})

        for j, policy in enumerate(policies):
            # Unpack policy
            media_literacy_intervention, ranking_intervention = policy

            # Set up data structure
            df_column = []

            for replication in range(n_replications):
                # Set up the model
                model = MisinfoModel(n_agents=n_agents,
                                     n_edges=n_edges,
                                     agent_ratio=scenario,
                                     media_literacy_intervention=media_literacy_intervention,
                                     ranking_intervention=ranking_intervention)

                # Save start data
                agents_belief_before = [agent.beliefs[str(Topic.VAX)] for agent in model.schedule.agents]

                # Run the model
                for tick in range(max_run_length):
                    model.step()

                # Save end data
                agents_belief_after = [agent.beliefs[str(Topic.VAX)] for agent in model.schedule.agents]
                # save data from this replication
                replication_data = (agents_belief_before, agents_belief_after)
                df_column.append(replication_data)

            # Create policy columns
            policy_column = pd.Series(df_column, name=str(policy))
            # Save policy column into the dataframe
            data = data.join(policy_column)

            # Printing
            print(f"policy {j} done")

        # Save scenario data into a csv file
        directory = os.getcwd()
        path = directory + '/results/'

        # file_name = "belief_distributions_before_after.csv"
        file_name = "belief_distr_" + str(scenario) + ".csv"
        data.to_csv(path + file_name)

        # # Printing
        # print(f"scenario {i} done")

    # Printing
    end_time = time.localtime(time.time())
    human_understandable_time = time.strftime('%Y-%m-%d %H:%M:%S', end_time)
    print(f"Ending at time: {human_understandable_time}")
    run_time = round(time.time() - start_time_seconds, 2)
    print(f"\nWith {max_run_length} steps, runtime is {run_time} seconds --> roughly {round(run_time/60/60, 2)} hours")

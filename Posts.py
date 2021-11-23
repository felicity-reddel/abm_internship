import random
from scipy.stats import skewnorm
from Enums import *


class Post:

    def __init__(self, unique_id, source, stances=None):
        self.unique_id = unique_id
        self.source = source
        if stances is None:
            self.stances = {}
        else:
            self.stances = stances  # stances represented in the post. {Topic: int_belief}
        self.visibility = self.estimate_visibility()
        self.factcheck_result = FactCheckResult.get_random()  # currently: TRUE or FALSE

    @staticmethod
    def sample_stances(max_n_topics=1, based_on_agent=None, skew=4) -> dict:
        """
        Generates and returns dict of stances for one post (i.e., topic & value):  {Topic.TOPIC1: int}

        :param based_on_agent:      the agent for whom the post is generated
        :param max_n_topics:        maximal number of topics in one post
        :param based_on_agent:      generate post-stances based on agent's current stances
        :param skew:                skewness of norm-distribution to sample from. if skew=0: normal distribution

        :return: dict of stances (i.e., topics with value)
        """
        # Sample how many topics should be included in post.
        n_topics = random.randint(1, max_n_topics)  # min. 1 topic per post

        # Sample stances (stance = topic with value)
        stances = {}
        for m in range(n_topics):

            # Pick topic
            topic = str(Topic.get_random())  # Ext: could adjust weights for diff. topics

            # Sample value on topic
            if based_on_agent:
                current_belief = based_on_agent.beliefs[topic]
                adjusted_skew = adjust_skew(current_belief, skew)
                value = skewnorm.rvs(a=adjusted_skew, loc=current_belief)
                value = max(min(value, 100), 0)
            else:
                value = random.randint(0, 100)
            stances[topic] = value

        return stances

    def estimate_visibility(self):
        """
        Estimates the visibility of the post.
        Here: just the extremeness of its stances
        :return:    float
        """

        extremeness = self.calculate_extremeness()
        engagement = extremeness

        return engagement

    def calculate_extremeness(self):
        """
        Calculates how extreme the post is.
        Here: the posts extremeness = the average extremeness of all its stances.
        :return: float
        """
        stances = self.stances.values()
        extremeness_values = []
        for stance in stances:
            extremeness = abs(100 - stance)
            extremeness_values.append(extremeness)

        avg_extremeness = sum(stances) / len(stances)

        # Scale to domain [0,1)
        avg_extremeness /= 100

        return avg_extremeness


def adjust_skew(current_belief, skew):
    """
    Adjusts the skew for the skewed normal distribution. --> skewed towards more extreme
    :param current_belief:  current belief of the agent
    :param skew:            how strongly to skew normal distribution (default: 4)
    :return:                adjusted skew (more extreme)
    """
    # skewed to the right
    adjusted = skew

    # skewed to the left
    if current_belief - 50 < 0:  # Ext: could parameterize the threshold of 50
        adjusted = -skew

    return adjusted

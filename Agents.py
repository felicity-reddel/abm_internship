import math
from mesa import Agent
from Posts import *
from Enums import *
import numpy as np


class BaseAgent(Agent):
    """Most simple agent to start with."""

    def __init__(self, unique_id, model):

        super().__init__(unique_id, model)

        self.beliefs = {}

        self.init_beliefs()
        self.followers = []
        self.following = []
        self.received_posts = []
        self.last_posts = []  # currently: all posts

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #   Step function: in two Stages.
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    def sample_number_of_posts(self):
        """
        Sample number of posts that an agent should share at one instant. It samples with a normal distribution based
        on this agent's vocality parameters (mu and sigma).
        :return:
            nr_of_posts: int
        """

        mu = self.vocality['mu']
        sigma = self.vocality['sigma']

        nr_of_posts = max(0, np.random.normal(mu, sigma, 1)[0])

        # rounding and converting to int
        nr_of_posts = round(nr_of_posts)

        return nr_of_posts

    def share_post_stage(self):
        """
        First part of the agent's step function. The first stage what all agents do in a time tick.
        """

        nr_of_posts = self.sample_number_of_posts()
        posts = []

        # Create posts
        for i in range(nr_of_posts):
            post = self.create_post()
            posts.append(post)

        # Share post to followers
        for follower in self.followers:
            follower.received_posts += posts

        # Save own posts
        self.last_posts += posts

    def update_beliefs_stage(self):
        """
        Second part of the agent's step function. The second stage what all agents do in an instant.
        """
        # Agent can only update beliefs if it received posts in the first stage of the time tick
        if len(self.received_posts) > 0:
            # Sample which of the received posts are actually seen (depends on ranking).
            seen_posts = self.sample_seen_posts()

            # For each seen post: judge truthfulness, then update beliefs (if post is judged as truthful).
            for post in seen_posts:

                # For each seen post: judge whether it is truthful.
                post_judged_as_truthful = self.judge_truthfulness(post)

                # For each seen post, which is judged as truthful: update beliefs.
                if post_judged_as_truthful:

                    # Update beliefs
                    self.update_beliefs_simple_sit(post)

        # empty received_posts again
        self.received_posts = []

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #  Simple SIT Belief-update
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    def update_beliefs_simple_sit(self, post):
        """
        Updates the beliefs of the agent based on a post.
        (The post which is passed is assumed to be seen by the agent.
        It is also assumed that the agent actually updates beliefs based on the post. I.e., in the current
        implementation, it is assumed that the agent judged the post to be truthful.)
        :param post:    Post, a seen post
        """

        # Calculate how the agent will update its beliefs
        updates = self.calculate_belief_update(post)

        # Update own beliefs  (after each seen post)
        for topic, update in updates.items():
            self.beliefs[topic] += update

    def calculate_belief_update(self, post) -> dict:
        """
        Calculates the agent's updates on the post.
        :param post:    Post
        :return:        dict, {topic: update}
        """

        # Prepare updates dict (to update after each seen post)
        updates = {}
        for topic in Topic:
            updates[str(topic)] = 0

        # Calculate updates
        for topic, post_value in post.stances.items():
            # Save previous beliefs
            prev_belief = self.beliefs[topic]

            # Calculate SIT components
            strength = self.calculate_strength(post)  # avg(relative n_followers, belief_similarity)
            # belief_similarity: between own_beliefs and source's_beliefs
            immediacy = self.calculate_immediacy(post)  # tie_strength
            n_sources = self.calculate_n_sources()  # (1 / n_following) * 100, [0,100]

            # Combine components
            social_impact = strength * immediacy * n_sources  # [0,100] * [0,100] * [0,100] --> [0,100^3]

            # Rescale
            max_increase = 0
            max_decrease = 0
            # downwards belief update
            if post_value < prev_belief:
                max_decrease = post_value - prev_belief
                social_impact *= -1  # to actually decrease belief
            # upwards belief update
            elif post_value > prev_belief:
                max_increase = post_value - prev_belief
            # no belief update
            else:  # post_value == prev_belief (--> max_increase & max_decrease stay 0)
                pass

            rescaled_social_impact = rescale(old_value=social_impact, new_domain=(max_decrease, max_increase))

            # Calculate update elasticity
            update_elasticity = self.calculate_update_elasticity(prev_belief)

            # Calculate final update for belief on topic
            update = rescaled_social_impact * update_elasticity
            updates[topic] += update

            # # Validation
            # if self.unique_id == 0:
            #     print(f'prev_belief: {prev_belief} \n'
            #           f'post value: {post_value} \n'
            #           f'max decrease: {max_decrease} \n'
            #           f'update_elasticity: {update_elasticity} \n'
            #           f'rescaled social impact: {rescaled_social_impact} \n'
            #           f'update: {update} \n')

        return updates

    def calculate_strength(self, post):
        """
        Calculates the strength component for the SIT belief update. In this case a combination of
        the relative number of followers and the belief_similarity between own belief & estimated belief of source.
        The other person's beliefs are estimated by looking at the stances of their last posts.
        :param post:        current post by other person (i.e., source)
        :return:            strength    float
        """
        rel_n_followers = self.get_relative_n_followers(post.source)
        belief_similarity = self.estimate_belief_similarity(post)
        strength = (rel_n_followers + belief_similarity)/2

        return strength

    def calculate_immediacy(self, post):
        """
        Calculates immediacy component for the SIT belief update as  tie strength (i.e., edge weight).
        :return:            immediacy value
        """

        tie_strength = self.model.G.edges[self.unique_id, post.source.unique_id, 0]['weight']  # Always key=0 because
        # maximally one connection in this direction possible.
        immediacy = tie_strength

        return immediacy

    def calculate_n_sources(self):
        """
        For the immediacy component of the SIT belief update, calculates the factor n_sources. The more accounts a user
        is following, the less they will update their beliefs based on each single one of them.
        :return:    float
        """
        n_following = len(self.following)
        n_sources = (1.0 / n_following) * 100

        return n_sources

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #  Averaging Belief-update  (Toy, for comparison)
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    def update_beliefs_avg(self, post):
        """
        Simplest update_beliefs function.
        New belief is average between own previous belief and the post's stance on the topic.
        """
        # Update towards post's stances
        for topic, value in post.stances.items():
            prev_belief = self.beliefs[topic]
            self.beliefs[topic] = (prev_belief + value) / 2

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #   General Helper-Functions
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    def init_beliefs(self):
        """
        Initialize for each topic a belief.
        """
        pass

    def create_post(self, based_on_beliefs=True):
        """
        Creates a new post. Either random or based on own stances.
        :return: Post
        """
        # Get post_id & post's stances
        id = self.model.post_id_counter
        # Increase post_id_counter
        self.model.post_id_counter += 1

        if based_on_beliefs:
            stances = Post.sample_stances(based_on_agent=self)
        else:
            stances = Post.sample_stances()

        # Create post
        post = Post(id, source=self, stances=stances)

        return post

    def sample_seen_posts(self):
        """
        Sample which of the received posts are actually seen/consumed by the agent.
        Result depends on the ranking implementation and whether the ranking intervention is applied.
        :return: list of seen posts: [Post]
        """
        seen_posts = []

        for post in self.received_posts:

            # If ranking intervention, update the post's visibility.
            if self.model.ranking_intervention:
                print('DIFFERENT RANKING!')
                post.visibility *= post.factcheck_result.value

            # "Coin toss"
            random_nr = random.random()
            if random_nr < post.visibility:
                seen_posts.append(post)

        return seen_posts

    def get_relative_n_followers(self, source):
        """
        Normalizes n_followers of agent.
        If 0.0: least n_followers in network.
        If 100.0: most n_followers in network.
        :return:    relative_n_followers    float   percentile
        """
        n_followers = len(list(self.model.G.successors(source.unique_id)))
        min_followers, max_followers = self.model.agents_data["n_followers_range"]

        relative_n_followers = (n_followers - min_followers) / (max_followers - min_followers)
        relative_n_followers = relative_n_followers * 100

        return relative_n_followers

    def estimate_belief_similarity(self, post):
        """
        For the immediacy component of the SIT belief update, estimate the belief similarity of self to other agent
        (only considering topics in this post).
        # EXTENSION: could also consider all topics mentioned in their last posts
        :param post:    Post
        :return:        float, similarity estimate
        """
        # Estimate other person's beliefs (on topics in current post)
        estimated_beliefs = {}

        for topic, value in post.stances.items():
            # Estimate their belief on 'topic' by looking at their last posts
            values = []
            for post in post.source.last_posts:
                if topic in post.stances:
                    value = post.stances[topic]
                    values.append(value)
            estimated_beliefs[topic] = sum(values) / len(values)

        # Calculate belief similarity (on beliefs in current post)
        similarities = []
        for topic, _ in post.stances.items():
            similarity = 100 - abs(self.beliefs[topic] - estimated_beliefs[topic])
            similarities.append(similarity)
        belief_similarity = sum(similarities) / len(similarities)

        return belief_similarity

    @staticmethod
    def calculate_update_elasticity(prev_belief, std_dev=15.0):
        """
        Calculates the update elasticity of an agent given its previous belief.
        Needed because it takes more until someone updates away from a belief in which they have high confidence
        (i.e., belief close extremes of the belief_domain). Beliefs don't update from e.g., 99 --> 20 due to one post.
        Analogously, when someone has low confidence in a belief (i.e., close to middle of belief_domain),
        it makes sense that they update more per post.

        :param prev_belief:             float, previous belief of an agent  (domain: belief_domain)
        :param std_dev:                 float or int                        (domain: belief_domain)
        :return: update_elasticity:     float                               (domain: [0,1])
        """
        mean = 50

        y = normal_distribution(x=prev_belief, mean=mean, std_dev=std_dev)

        # Scale y, such that at middle (e.g., 50), the update elasticity is 1:
        max_elasticity = normal_distribution(x=mean, mean=mean, std_dev=std_dev)
        update_elasticity = y / max_elasticity

        return update_elasticity

    def judge_truthfulness(self, post):
        """
        Simple version of judging the truthfulness of a post.
        Agents with high media literacy judge true posts as true, and false posts as false.
        Agents with low media literacy judge all posts as true.
        :param post: Post
        :return: boolean, whether the post is judged as true or false
        """

        # A post is only judged as NOT truthful if:
        #       - the post's factcheck_result is false
        #   AND
        #       - the agent's media literacy is high
        judged_truthfulness = True
        if self.media_literacy.__eq__(MediaLiteracy.HIGH) and post.factcheck_result.__eq__(FactCheckResult.FALSE):
            judged_truthfulness = False

        return judged_truthfulness


class NormalUser(BaseAgent):

    def __init__(self, unique_id, model):

        super().__init__(unique_id, model)

        self.vocality = {'mu': 2, 'sigma': 0.7}  # This is used to sample nr of posts
        self.media_literacy = MediaLiteracy.get_random()  # {LOW, HIGH}

    def init_beliefs(self):
        """
        Initialize for each topic a random belief.
        """
        for topic in Topic:
            self.beliefs[str(topic)] = self.random.randint(0, 100)


class Disinformer(BaseAgent):

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

        self.vocality = {'mu': 10, 'sigma': 0.7}  # This is used to sample nr of posts
        self.media_literacy = MediaLiteracy.LOW

    def init_beliefs(self):
        """
        Initialize for each topic a random extreme belief.
        """
        for topic in Topic:
            self.beliefs[str(topic)] = self.random.randint(0, 10)

# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
#   More independent Helper-Functions
# ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––


def rescale(old_value, old_domain=(-1000000, 1000000), new_domain=(0, 100)):
    """
    Rescales a value from one range to another.
    By default from range [-100ˆ3,100ˆ3] to [-100,100].

    :param old_value:   float
    :param old_domain:   tuple, (min_old_range, max_old_range)
    :param new_domain:   tuple, (min_new_range, max_new_range)
    :return: new_value: float
    """
    old_min, old_max = old_domain

    if old_value < 0:
        old_max = 0  # we already know that it should decrease, thus old_max = 0  and  new_max = 0
        new_max = 0
        new_min, _ = new_domain
        old_range = old_max - old_min
        new_range = new_max - new_min

        new_value = (((old_value - old_min) * new_range) / old_range) + new_min

    elif old_value > 0:
        old_min = 0  # we already know that it should increase, thus old_min = 0   and  new_min = 0
        new_min = 0
        _, new_max = new_domain
        old_range = old_max - old_min
        new_range = new_max - new_min

        new_value = (((old_value - old_min) * new_range) / old_range) + new_min
    else:
        new_value = 0

    return new_value


def normal_distribution(x, mean=50.0, std_dev=30.0):
    """
    Returns which y corresponds to the provided x value and parameter of the normal distribution.
    :param x:       float
    :param mean:    float
    :param std_dev: float
    :return: y      float
    """

    dividend = math.exp((-(x - mean) ** 2 / (2 * std_dev ** 2)))
    divisor = math.sqrt(2 * math.pi) * std_dev

    y = dividend / divisor

    return y

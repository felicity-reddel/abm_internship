from mesa import Agent
from Posts import *


class BaseAgent(Agent):
    """Most simple agent to start with."""

    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)

        self.beliefs = {}
        self.tendency_to_share = random.random()  # Ext: adjust for different kind of agents
        self.init_beliefs()
        self.followers = []
        self.following = []
        self.will_post = True if random.random() < self.tendency_to_share else False
        self.received_posts = []
        self.last_posts = []  # currently: all posts

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #   Step function: in two Stages.
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    def share_post_stage(self):

        # Decide whether to post
        will_post = True if random.random() < self.tendency_to_share else False

        # Create post & share
        if will_post:
            post = self.create_post()
            self.last_posts.append(post)

            # Share post to followers
            for follower in self.followers:
                follower.received_posts.append((post, self))  # self = source of post

    def update_beliefs_stage(self):
        if len(self.received_posts) > 0:
            # Do the update
            # self.update_beliefs_avg()
            self.update_beliefs_simple_sit()

        # empty self.received_posts again
        self.received_posts = []

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #   General Helper-Functions
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    def update_beliefs_avg(self):
        """
        Simplest update_beliefs function. Based on received posts in this step/tick.
        New belief is average between own previous belief and the post's stance on the topic.
        """

        for post, _ in self.received_posts:

            # Update towards post's stances
            for topic, value in post.stances.items():
                prev_belief = self.beliefs[topic]
                self.beliefs[topic] = (prev_belief + value) / 2

    def update_beliefs_simple_sit(self):
        # Prepare updates dict
        updates = {}
        for topic in Topic:
            updates[topic] = 0

        # Calculate updates for each post and topic
        for post, source in self.received_posts:
            for topic, post_value in post.stances.items():
                prev_belief = self.beliefs[topic]

                # Calculate SIT components
                strength = self.calculate_strength(source)
                # strength: weighted_avg(relative n_followers, belief_similarity)
                #                   relative n_followers of source: [0,100]
                #                   belief_similarity: 100 - abs(own_belief–friend_belief), [0, 100]
                immediacy = self.calculate_immediacy(post, source)  # tie_strength
                # tie_strength: edge_weight between agent & friend, [0,100]
                n_sources = self.calculate_n_sources()  # (1 / n_following) * 100, [0,100]

                # Combine components
                social_impact = strength * immediacy * n_sources
                # social_impact = (strength + immediacy + n_sources) / 3
                direction = -1 if post_value < prev_belief else 1

                update = social_impact * direction
                updates[topic] += update

        # Update own beliefs
        for topic, update in updates.items():
            prev_belief = self.beliefs[topic]
            # Make sure belief stays in [0,100]-range
            self.beliefs[topic] = max(0, min(100, prev_belief+update))

    # Lesson from update_beliefs_simple_sit:
    # - Takes a lot longer to converge.
    # - Most agents end up with quite strong beliefs.
    # - Outcome strongly depends on initial conditions, i.e., initial belief distribution (randomly sampled here).

    def init_beliefs(self):
        """
        Initialize for each topic a random belief.
        :return:
        """
        for topic in Topic:
            self.beliefs[topic] = self.random.randint(0, 100)

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
        post = Post(id, stances)

        return post

    def print_vax_decision(self, threshold=50.0):
        """
        Print the vaccination_willingness value and the corresponding decision.
        :param threshold:   float, decision-threshold for/against getting vaccinated
        """
        # Print value and decision
        decision = "vaccine"
        if self.beliefs[Topic.VAX] <= threshold:
            decision = "NO VACCINE !!1!"

        print("Agent " + str(self.unique_id) + ": " + str(self.beliefs[Topic.VAX])
              + " --> " + decision)

    def get_neighbors(self, node=None) -> list:  # list of agents
        """
        Returns all neighbor-agents of a node. If no specific node is provided, the own neighbors are returned.
        :return:    list of agents in neighboring nodes
        """

        # Get neighboring nodes  (i.e., list of their ids, integers)
        if not node:  # If no node provided, get own neighbors.
            neighbor_nodes = self.model.grid.get_neighbors(self.unique_id)
        else:
            neighbor_nodes = self.model.grid.get_neighbors(node)

        # Get agents from neighboring nodes
        neighbor_agents = []
        for (_, agent) in self.model.G.nodes.data("agent"):
            if agent.pos in neighbor_nodes:
                neighbor_agents.append(agent)

        return neighbor_agents

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #   Toy Interaction: 1-on-1, Certainty-based update. Without Posts.
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    def toy_interaction(self):
        """ Toy interaction step method.
        An agent only interacts with one randomly selected neighbor.
        The agent who was less certain updates very strongly towards the more certain agent's belief.
        The agent who was more certain becomes even a bit more certain (due to the strong update of the other agent)."""

        # Pick neighbor
        neighbors = self.neighbors
        other_agent = self.random.choice(neighbors)
        # Determine who is more certain
        more_certain_agent, less_certain_agent = self.get_more_certain_agent(other_agent)
        # Update stances accordingly
        self.toy_update_beliefs(more_certain_agent, less_certain_agent)

    def get_more_certain_agent(self, other_agent):
        """ For toy_interaction. Determine which agent is more/less certain and return them. """
        # Determine which agent was more certain
        # more certain --> further away from middle (i.e., from 50)
        more_certain_agent = other_agent
        less_certain_agent = self
        if abs(self.beliefs[Topic.VAX] - 50) > abs(other_agent.beliefs[Topic.VAX] - 50):
            more_certain_agent = self
            less_certain_agent = other_agent
        return more_certain_agent, less_certain_agent

    @staticmethod
    def toy_update_beliefs(more_certain_agent, less_certain_agent):
        """ For toy_interaction. Determine new belief-values and assign them for both agents.
        :type more_certain_agent: agent object, agent with more extreme belief
        :type less_certain_agent: agent object, agent with less extreme belief
        """
        # Update agents' stances
        # was less certain --> update to average belief of both agents
        less_certain_agent.beliefs[Topic.VAX] = round(
            (more_certain_agent.beliefs[Topic.VAX] + less_certain_agent.beliefs[Topic.VAX]) / 2)
        # was more certain --> become even more certain of belief
        if more_certain_agent.beliefs[Topic.VAX] >= 50:
            more_certain_agent.beliefs[Topic.VAX] = more_certain_agent.beliefs[Topic.VAX] + 1
            # Introduce upper-bound of 100
            # = min(100, more_certain_agent.beliefs[Topic.VAX] + 1)
        else:
            more_certain_agent.beliefs[Topic.VAX] = more_certain_agent.beliefs[Topic.VAX] - 1
            # Introduce lower-bound of 0
            # = max(0, more_certain_agent.beliefs[Topic.VAX] - 1)

    # Lesson from Toy:
    # - Outcome strongly depends on initial conditions, i.e., initial belief distribution (randomly sampled here).
    #   Either all/most agents get the vaccine or all/most don't. Very extreme values.

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #  Toy Interaction: Many-on-1, Average-based update. Without Posts.
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

    def toy_adjust_to_average(self):
        # Get neighbors' stances
        neighbors_beliefs = [neighbor.beliefs[Topic.VAX] for neighbor in self.neighbors]

        # Update own belief towards average neighbor-belief
        avg_neighbor_belief = sum(neighbors_beliefs) / len(neighbors_beliefs)
        self.beliefs[Topic.VAX] = (self.beliefs[Topic.VAX] + avg_neighbor_belief) / 2

    # Lesson from toy_adjust_to_average:
    # - Outcome strongly depends on initial conditions, i.e., initial belief distribution (randomly sampled here).
    #   Either all/most agents get the vaccine or all/most don't. Moderate values.

    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––
    #  Simple SIT Belief-update
    # ––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––––

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

    def calculate_strength(self, source):
        """
        Calculates the strength component for the SIT belief update. In this case just the relative number of followers.
        :return:    strength    float
        """
        strength = self.get_relative_n_followers(source)
        return strength

    def calculate_immediacy(self, post, source):
        """
        Calculates immediacy component for the SIT belief update as a combination of tie strength (i.e., edge weight)
        and similarity of beliefs. The other person's beliefs are estimated by looking at the stances of their last
        posts.
        :param post:        current post by other person
        :param source:      other person
        :return:            immediacy value
        """

        belief_similarity = self.estimate_belief_similarity(post, source)
        tie_strength = self.model.G.edges[self.unique_id, source.unique_id, 0]['weight']  # Always key=0 because
        # maximally one connection in this direction possible.
        immediacy = (belief_similarity + tie_strength)/2

        return immediacy

    def estimate_belief_similarity(self, post, source):
        """
        For the immediacy component of the SIT belief update, estimate the belief similarity of self to other agent
        (only considering topics in this post).
        # EXTENSION: could also consider all topics mentioned in their last posts
        :param post:    Post
        :param source:  Agent
        :return:        float, similarity estimate
        """
        # Estimate other person's beliefs (on topics in current post)
        estimated_beliefs = {}

        for topic, value in post.stances.items():
            # Estimate their belief on 'topic' by looking at their last posts
            values = []
            for post in source.last_posts:
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

        # print(f'belief_similarity: {belief_similarity}')
        return belief_similarity

    def calculate_n_sources(self):
        """
        For the immediacy component of the SIT belief update, calculates the factor n_sources. The more accounts a user
        is following, the less they will update their beliefs based on each single one of them.
        :return:    float
        """
        n_following = len(self.following)
        n_sources = (1.0 / n_following) * 100

        return n_sources


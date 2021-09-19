from enum import Enum


class Post:

    def __init__(self, unique_id, messages={}, fact_check_result=False):
        self.unique_id = unique_id
        self.messages = messages
        # self.fact_check_result = fact_check_result


class Topic(Enum):
    VAX = 1

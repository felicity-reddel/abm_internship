from enum import Enum
import random


class Topic(Enum):
    """
    Implemented Topics (for stances of posts & beliefs of agents).
    Easily extendable to include more topics (e.g., MASKS, EVOLUTION, etc.)
    """
    def __eq__(self, o: object) -> bool:
        if self.value is o.value:
            return True
        else:
            return False

    VAX = 0
    # MASKS = 1
    # EVOLUTION = 2

    @staticmethod
    def get_random():
        result = random.choice(list(Topic))
        return result


class FactCheckResult(Enum):
    """
    Enumeration representing the a factcheck would have (i.e., the ground truth).
    Easily extendable to include more options (e.g., MISLEADING)

    Each value represents the adjustment in visibility.
    i.e., if ranking_invervention is on AND FactCheckResult.FALSE --> post has only 50% of its previous visibility.
    """
    def __eq__(self, o: object) -> bool:
        if self.value is o.value:
            return True
        else:
            return False

    FALSE = 0.5
    TRUE = 1
    # MISLEADING = 0.75

    @staticmethod
    def get_random():
        result = random.choice(list(FactCheckResult))
        return result


class MediaLiteracy(Enum):
    """
    Media Literacy Levels
    """
    def __eq__(self, o: object) -> bool:
        if self.value is o.value:
            return True
        else:
            return False

    LOW = 0
    HIGH = 1

    @staticmethod
    def get_random():
        result = random.choice(list(MediaLiteracy))
        return result


class SelectAgentsBy(Enum):
    """
    Possibilities to select agents. E.g., for who will by empowered by the Media Literacy Intervention.
    Easily extendable to e.g., pick agents based on an agent-characteristic (e.g., age, if age is an agent attribute).
    """

    def __eq__(self, o: object) -> bool:
        if self.value is o.value:
            return True
        else:
            return False

    RANDOM = 0
    # HIGH_AGE = 1
    # LOW_AGE = 2


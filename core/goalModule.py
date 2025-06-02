import math
from typing import Callable, Dict, List, Optional

class Goal:
    def __init__(
        self,
        name: str,
        urgency_fn: Callable[[float], float],
        utility_fn: Callable[[Dict], float],
        dependencies: Optional[List['Goal']] = None
    ):
        self.name = name
        self.urgency_fn = urgency_fn
        self.utility_fn = utility_fn
        self.dependencies = dependencies or []

    def urgency(self, t: float) -> float:
        return self.urgency_fn(t)

    def utility(self, state: Dict) -> float:
        return self.utility_fn(state)

    def effective_value(self, t: float, state: Dict) -> float:
        return self.urgency(t) * self.utility(state)

    def describe(self, t: float, state: Dict) -> str:
        return (f"Goal: {self.name}\n"
                f"  Urgency(t={t:.2f}): {self.urgency(t):.4f}\n"
                f"  Utility(state): {self.utility(state):.4f}\n"
                f"  Effective Value: {self.effective_value(t, state):.4f}")

# Example urgency/utility functions

def linear_urgency(t: float) -> float:
    return min(1.0, t / 10.0)

def curiosity_utility(state: Dict) -> float:
    return state.get("novelty", 0.5)

def safety_utility(state: Dict) -> float:
    return 1.0 - state.get("danger", 0.5)

# Concrete Goals

class EatFoodGoal(Goal):
    def __init__(self, name="Eat"):
        super().__init__(name, linear_urgency, lambda s: 1.0 - s.get("hunger", 0.5))

class SocialBondingGoal(Goal):
    def __init__(self, name="Bond"):
        super().__init__(name, linear_urgency, lambda s: s.get("affection", 0.5))

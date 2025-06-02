from typing import Callable, List, Optional, Set
import math

class Goal:
    def __init__(
        self,
        name: str,
        urgency_function: Callable[[float], float],
        utility_function: Callable[[dict], float],
        dependencies: Optional[List['Goal']] = None,
        weight: float = 1.0
    ):
        self.name = name
        self.urgency_function = urgency_function
        self.utility_function = utility_function
        self.dependencies = dependencies if dependencies else []
        self.weight = weight

    def urgency(self, t: float) -> float:
        """
        Compute urgency at time t (range 0 to 1)
        """
        try:
            u = self.urgency_function(t)
            return max(0.0, min(1.0, u))
        except Exception as e:
            print(f"[Urgency Error] Goal '{self.name}': {e}")
            return 0.0

    def utility(self, state: dict) -> float:
        """
        Compute utility given a state (arbitrary dict)
        """
        try:
            return self.utility_function(state)
        except Exception as e:
            print(f"[Utility Error] Goal '{self.name}': {e}")
            return 0.0

    def effective_value(self, t: float, state: dict, visited: Optional[Set[str]] = None) -> float:
        """
        Recursive effective value: urgency * utility * weight + sum of dependencies' effective values

        Args:
            t: current time
            state: current environment state
            visited: set of visited goal names to detect cycles

        Returns:
            Effective float value
        """
        if visited is None:
            visited = set()
        if self.name in visited:
            # Prevent infinite recursion due to cycles
            print(f"[Cycle Warning] Goal '{self.name}' already visited. Skipping to avoid recursion.")
            return 0.0
        visited.add(self.name)

        base = self.urgency(t) * self.utility(state) * self.weight
        for dep in self.dependencies:
            base += dep.effective_value(t, state, visited)
        return base

    def describe(self, t: float, state: dict) -> str:
        """
        Textual summary of current goal status
        """
        return (
            f"Goal: {self.name}\n"
            f"  Urgency: {self.urgency(t):.2f}\n"
            f"  Utility: {self.utility(state):.2f}\n"
            f"  Weight: {self.weight:.2f}\n"
            f"  Effective Value: {self.effective_value(t, state):.2f}\n"
            f"  Dependencies: {[g.name for g in self.dependencies]}\n"
        )


# Example urgency and utility functions

def linear_urgency(t: float) -> float:
    return min(1.0, max(0.0, t / 10.0))

def curiosity_utility(state: dict) -> float:
    return state.get('novelty', 0.0) * 2.0

def safety_utility(state: dict) -> float:
    return 1.0 - state.get('danger', 0.0)


# Example instantiation for quick testing

def example_goal_tree() -> Goal:
    explore = Goal("Explore", linear_urgency, curiosity_utility)
    survive = Goal("Survive", linear_urgency, safety_utility)
    master = Goal("MasterGoal", linear_urgency, lambda s: 0.5, dependencies=[explore, survive])
    return master


if __name__ == "__main__":
    t = 5.0
    state = {"novelty": 0.8, "danger": 0.3}
    goal = example_goal_tree()
    print(goal.describe(t, state))

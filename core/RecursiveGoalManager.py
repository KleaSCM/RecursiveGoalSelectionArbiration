from typing import List, Dict, Union
import math

class Goal:
    def __init__(self, name: str):
        self.name = name
        self.subgoals: List['Goal'] = []

    def evaluate(self, t: float, state: dict) -> float:
        raise NotImplementedError(f"evaluate not implemented for {self.name}")

    def evaluate_lyapunov(self, t: float, state: dict) -> float:
        return 0.0  # Default: neutral stability

    def commitment_curve(self, t: float) -> float:
        return 1.0  # Fully committed by default

    def trait_modifiers(self, state: dict) -> Dict[str, float]:
        return {}  # No trait influence by default


class GoalArbitrator:
    def __init__(self, mode: str = 'softmax', temperature: float = 1.0):
        self.mode = mode
        self.temperature = temperature

    def select(self, expected_values: Dict[Goal, float]) -> Union[Goal, Dict[Goal, float]]:
        if not expected_values:
            return {}

        if self.mode == 'max':
            return max(expected_values.items(), key=lambda x: x[1])[0]

        if self.mode == 'softmax':
            exp_vals = {g: math.exp(v / self.temperature) for g, v in expected_values.items()}
            total = sum(exp_vals.values())
            return {g: v / total for g, v in exp_vals.items()}

        raise ValueError(f"Unknown arbitration mode: {self.mode}")


class RecursiveGoalManager:
    def __init__(self, root_goal: Goal, arbitrator: GoalArbitrator):
        self.root_goal = root_goal
        self.arbitrator = arbitrator
        self.t = 0.0

    def step(self, dt: float, state: dict) -> float:
        self.t += dt
        return self._evaluate_recursive(self.root_goal, state, level=0)

    def _evaluate_recursive(self, goal: Goal, state: dict, level: int) -> float:
        if not goal.subgoals:
            return goal.evaluate(self.t, state)

        expected_values = {sg: sg.evaluate(self.t, state) for sg in goal.subgoals}
        selected = self.arbitrator.select(expected_values)

        if isinstance(selected, dict):
            return sum(w * self._evaluate_recursive(g, state, level + 1) for g, w in selected.items())
        else:
            return self._evaluate_recursive(selected, state, level + 1)

    def reset(self):
        self.t = 0.0

    def inject_goal(self, goal: Goal, parent: Goal = None):
        target = parent or self.root_goal
        target.subgoals.append(goal)


# Example concrete goal implementations
class EatFoodGoal(Goal):
    def evaluate(self, t, state):
        hunger = state.get("hunger", 0.5)
        return 1.0 - hunger

class SocialBondingGoal(Goal):
    def evaluate(self, t, state):
        affection = state.get("affection", 0.5)
        return affection


# Setup example usage
def build_example_manager():
    root = Goal("LiveWell")
    eat = EatFoodGoal("Eat")
    bond = SocialBondingGoal("Bond")
    root.subgoals = [eat, bond]

    arbitrator = GoalArbitrator(mode='softmax', temperature=0.5)
    manager = RecursiveGoalManager(root_goal=root, arbitrator=arbitrator)
    return manager
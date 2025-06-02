from typing import List, Dict, Union, Optional
import math


class Goal:
    """
    Abstract base class representing a cognitive or behavioral goal.

    Attributes:
        name (str): Identifier for the goal.
        subgoals (List[Goal]): Hierarchical subgoals of this goal.
    """

    def __init__(self, name: str):
        self.name: str = name
        self.subgoals: List['Goal'] = []

    def evaluate(self, t: float, state: dict) -> float:
        """
        Compute the utility or value of this goal at time t given the current state.

        Args:
            t (float): Current time or timestep.
            state (dict): State dictionary representing internal/external conditions.

        Returns:
            float: The expected value or utility of this goal.
        """
        raise NotImplementedError(f"Goal.evaluate not implemented for {self.name}")

    def evaluate_lyapunov(self, t: float, state: dict) -> float:
        """
        Compute Lyapunov stability metric for this goal.

        Lyapunov value > 0 implies local stability (attractor),
        < 0 implies instability, and 0 neutral.

        Args:
            t (float): Current time.
            state (dict): Current state.

        Returns:
            float: Stability measure.
        """
        return 0.0  # Default: neutral stability

    def commitment_curve(self, t: float) -> float:
        """
        Commitment function representing the persistence or priority curve over time.

        Args:
            t (float): Current time.

        Returns:
            float: Commitment value in [0,1].
        """
        return 1.0  # Fully committed by default

    def trait_modifiers(self, state: dict) -> Dict[str, float]:
        """
        Modify goal evaluation based on traits or contextual factors.

        Args:
            state (dict): Current state containing trait values.

        Returns:
            Dict[str, float]: Dictionary of trait influences and their weights.
        """
        return {}  # Default no trait influence


class GoalArbitrator:
    """
    Arbitration mechanism to select among competing goals.

    Supports 'max' (deterministic) and 'softmax' (probabilistic) modes.

    Attributes:
        mode (str): Arbitration mode. Options: 'max', 'softmax'.
        temperature (float): Temperature parameter for softmax smoothing.
    """

    def __init__(self, mode: str = 'softmax', temperature: float = 1.0):
        if mode not in ('max', 'softmax'):
            raise ValueError(f"Unknown arbitration mode: {mode}")
        self.mode: str = mode
        self.temperature: float = temperature

    def select(self, expected_values: Dict[Goal, float]) -> Union[Goal, Dict[Goal, float]]:
        """
        Select a goal or distribution over goals given their expected values.

        Args:
            expected_values (Dict[Goal, float]): Mapping from goals to their expected values.

        Returns:
            Union[Goal, Dict[Goal, float]]: Selected goal (max mode) or distribution (softmax).
        """
        if not expected_values:
            return {}

        if self.mode == 'max':
            # Deterministically pick the goal with highest expected value
            selected_goal = max(expected_values.items(), key=lambda x: x[1])[0]
            return selected_goal

        elif self.mode == 'softmax':
            max_val = max(expected_values.values())
            exp_vals = {
                g: math.exp((v - max_val) / self.temperature)
                for g, v in expected_values.items()
            }
            total = sum(exp_vals.values())
            if total == 0:
                # Avoid division by zero, fallback to uniform
                n = len(exp_vals)
                return {g: 1/n for g in exp_vals}
            normalized = {g: val / total for g, val in exp_vals.items()}
            return normalized


class RecursiveGoalManager:
    """
    Manages a hierarchy of goals recursively, using an arbitrator to select and
    evaluate goals over time.

    Attributes:
        root_goal (Goal): Top-level root goal.
        arbitrator (GoalArbitrator): Arbitration mechanism for goal selection.
        t (float): Internal timestep counter.
    """

    def __init__(self, root_goal: Goal, arbitrator: GoalArbitrator):
        self.root_goal: Goal = root_goal
        self.arbitrator: GoalArbitrator = arbitrator
        self.t: float = 0.0

    def step(self, dt: float, state: dict) -> float:
        """
        Advance time by dt and evaluate the goal hierarchy recursively.

        Args:
            dt (float): Time increment.
            state (dict): Current system state.

        Returns:
            float: Aggregated expected value of the root goal after evaluation.
        """
        self.t += dt
        return self._evaluate_recursive(self.root_goal, state, level=0)

    def _evaluate_recursive(self, goal: Goal, state: dict, level: int) -> float:
        """
        Recursively evaluate a goal and its subgoals according to the arbitrator.

        Args:
            goal (Goal): Current goal node.
            state (dict): Current state.
            level (int): Recursion depth level.

        Returns:
            float: Expected value of the evaluated goal subtree.
        """
        if not goal.subgoals:
            # Leaf goal: evaluate directly
            return goal.evaluate(self.t, state)

        # Evaluate each subgoal's expected value
        expected_values = {sg: sg.evaluate(self.t, state) for sg in goal.subgoals}
        # Arbitration decides which goal(s) to prioritize
        selected = self.arbitrator.select(expected_values)

        if isinstance(selected, dict):
            # Softmax: weighted sum of subgoals
            total_value = 0.0
            for subgoal, weight in selected.items():
                # Recursive evaluation weighted by arbitrator distribution
                subval = self._evaluate_recursive(subgoal, state, level + 1)
                total_value += weight * subval
            return total_value

        else:
            # Max mode: single selected goal
            return self._evaluate_recursive(selected, state, level + 1)

    def reset(self) -> None:
        """Reset internal time to zero."""
        self.t = 0.0

    def inject_goal(self, goal: Goal, parent: Optional[Goal] = None) -> None:
        """
        Insert a new goal into the goal hierarchy under a specified parent.

        Args:
            goal (Goal): Goal to inject.
            parent (Optional[Goal]): Parent goal to attach to. Defaults to root goal.
        """
        target = parent or self.root_goal
        target.subgoals.append(goal)


# --- Example concrete goal implementations with trait modifiers, commitment, stability ---

class EatFoodGoal(Goal):
    def evaluate(self, t: float, state: dict) -> float:
        hunger = state.get("hunger", 0.5)  # 0 = full, 1 = starving
        base_value = hunger  # More hunger means higher value
        trait_influence = self.trait_modifiers(state)
        modifier = sum(trait_influence.values())
        commitment = self.commitment_curve(t)
        return base_value * (1 + modifier) * commitment

    def trait_modifiers(self, state: dict) -> Dict[str, float]:
        # Example: if "food_aversion" trait exists and is high, reduce motivation
        food_aversion = state.get("food_aversion", 0.0)
        return {"food_aversion": -food_aversion}

    def commitment_curve(self, t: float) -> float:
        # Hunger urgency grows over time without food
        return min(1.0, 0.1 + 0.9 * (t / 10.0))  # saturates at 1 over 10 units time

    def evaluate_lyapunov(self, t: float, state: dict) -> float:
        hunger = state.get("hunger", 0.5)
        # Positive Lyapunov implies goal stability if hunger high
        return 0.5 if hunger > 0.7 else -0.5


class SocialBondingGoal(Goal):
    def evaluate(self, t: float, state: dict) -> float:
        affection = state.get("affection", 0.5)
        base_value = affection
        trait_influence = self.trait_modifiers(state)
        modifier = sum(trait_influence.values())
        commitment = self.commitment_curve(t)
        return base_value * (1 + modifier) * commitment

    def trait_modifiers(self, state: dict) -> Dict[str, float]:
        # Example: "social_anxiety" reduces bonding motivation
        social_anxiety = state.get("social_anxiety", 0.0)
        return {"social_anxiety": -social_anxiety}

    def commitment_curve(self, t: float) -> float:
        # For simplicity, constant commitment
        return 1.0

    def evaluate_lyapunov(self, t: float, state: dict) -> float:
        affection = state.get("affection", 0.5)
        # Stability increases with high affection
        return 0.7 if affection > 0.6 else -0.3


# --- Example Usage Setup ---

def build_example_manager() -> RecursiveGoalManager:
    """
    Construct example RecursiveGoalManager with 'LiveWell' root goal and two subgoals.

    Returns:
        RecursiveGoalManager: Manager with preset goals and arbitrator.
    """
    root = Goal("LiveWell")
    eat = EatFoodGoal("Eat")
    bond = SocialBondingGoal("Bond")
    root.subgoals = [eat, bond]

    arbitrator = GoalArbitrator(mode='softmax', temperature=0.5)
    manager = RecursiveGoalManager(root, arbitrator)
    return manager


if __name__ == "__main__":
    mgr = build_example_manager()
    # Example state: starving and moderately affectionate, no aversion/anxiety
    example_state = {"hunger": 0.9, "food_aversion": 0.0, "affection": 0.5, "social_anxiety": 0.0}
    val = mgr.step(dt=1.0, state=example_state)
    print(f"Aggregated expected value at t={mgr.t}: {val:.3f}")

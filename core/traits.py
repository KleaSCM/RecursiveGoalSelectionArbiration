from abc import ABC, abstractmethod
from typing import Dict, List, Optional
from .goalModule import Goal



class GoalTrait(ABC):
    """
    Abstract base class for all goal traits.
    Traits may affect urgency, utility, and final value based on context, dependencies, or internal logic.
    """

    def adjust_urgency(self, base_urgency: float, *, t: float, goal: Goal) -> float:
        """Override to modulate urgency dynamically."""
        return base_urgency

    def adjust_utility(self, base_utility: float, *, state: Dict, goal: Goal) -> float:
        """Override to modulate utility dynamically."""
        return base_utility

    @abstractmethod
    def modify(
        self,
        *,
        base: float,
        urgency: float,
        utility: float,
        dependencies: List[Goal],
        dep_value: float,
        state: Dict,
        goal: Goal,
        t: float
    ) -> float:
        """
        Modify the final effective value based on trait logic.
        This function is where all modulation logic is implemented.
        """
        pass

# -----------------------------
# Example Traits
# -----------------------------

class GreedyTrait(GoalTrait):
    """
    Amplifies high-utility goals at the expense of urgency.
    Used in agents that prioritize value-rich actions regardless of time pressure.
    """

    def modify(self, *, base, urgency, utility, dependencies, dep_value, state, goal, t):
        return 0.2 * (utility ** 2) - 0.05 * urgency


class DependencyAmplifierTrait(GoalTrait):
    """
    Increases effective value of the goal when dependent goals are active.
    Useful for hierarchical or bundle-linked tasks.
    """

    def modify(self, *, base, urgency, utility, dependencies, dep_value, state, goal, t):
        return 0.1 * dep_value


class TimeDecayTrait(GoalTrait):
    """
    Applies exponential decay to urgency over time.
    Models fatigue or temporal irrelevance.
    """

    def adjust_urgency(self, base_urgency, *, t, goal):
        decay_factor = 0.95 ** t
        return base_urgency * decay_factor

    def modify(self, *, base, urgency, utility, dependencies, dep_value, state, goal, t):
        return 0.0  # All modulation handled via adjust_urgency


class StateBoostTrait(GoalTrait):
    """
    Boosts value when a particular key in the state meets a condition.
    Example: increase value if 'energy' > 0.8 or 'mood' is 'happy'.
    """

    def __init__(self, key: str, threshold: float, boost: float):
        self.key = key
        self.threshold = threshold
        self.boost = boost

    def modify(self, *, base, urgency, utility, dependencies, dep_value, state, goal, t):
        if state.get(self.key, 0) >= self.threshold:
            return self.boost
        return 0.0


class EntropicStabilizerTrait(GoalTrait):
    """
    Penalizes volatile goals whose utility or urgency fluctuate strongly.
    Assumes state includes a moving window of previous values (e.g., in a larger framework).
    """

    def modify(self, *, base, urgency, utility, dependencies, dep_value, state, goal, t):
        volatility = state.get('volatility', {}).get(goal.name, 0.0)
        return -0.1 * volatility


class UrgencyClamperTrait(GoalTrait):
    """
    Caps urgency to avoid frantic goal pursuit.
    """

    def adjust_urgency(self, base_urgency, *, t, goal):
        return min(base_urgency, 1.0)


class RecursiveRewardTrait(GoalTrait):
    """
    Increases goal value if the agent has historically succeeded at it.
    Encourages stable recursive habits and behavioral convergence.
    """

    def modify(self, *, base, urgency, utility, dependencies, dep_value, state, goal, t):
        success_count = state.get('success_history', {}).get(goal.name, 0)
        return 0.05 * success_count


class TraitStack(GoalTrait):
    """
    Combines multiple traits into a unified trait object.
    Allows arbitrarily composable behavior.
    """

    def __init__(self, traits: List[GoalTrait]):
        self.traits = traits

    def adjust_urgency(self, base_urgency, *, t, goal):
        for trait in self.traits:
            base_urgency = trait.adjust_urgency(base_urgency, t=t, goal=goal)
        return base_urgency

    def adjust_utility(self, base_utility, *, state, goal):
        for trait in self.traits:
            base_utility = trait.adjust_utility(base_utility, state=state, goal=goal)
        return base_utility

    def modify(self, *, base, urgency, utility, dependencies, dep_value, state, goal, t):
        return sum(
            trait.modify(
                base=base,
                urgency=urgency,
                utility=utility,
                dependencies=dependencies,
                dep_value=dep_value,
                state=state,
                goal=goal,
                t=t
            ) for trait in self.traits
        )

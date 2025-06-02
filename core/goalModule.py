import math
from typing import Callable, Dict, List, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    # Only import for type checking (avoids runtime circular import)
    from .traits import GoalTrait

class Goal:
    def __init__(
        self,
        name: str,
        urgency_fn: Callable[[float], float],
        utility_fn: Callable[[Dict], float],
        dependencies: Optional[List['Goal']] = None,
        traits: Optional[List['GoalTrait']] = None  # Use string literal to delay evaluation
    ):
        self.name = name
        self.urgency_fn = urgency_fn
        self.utility_fn = utility_fn
        self.dependencies = dependencies or []
        self.traits = traits or []

    def urgency(self, t: float, state: Optional[Dict] = None) -> float:
        base_urgency = self.urgency_fn(t)
        for trait in self.traits:
            if hasattr(trait, 'adjust_urgency'):
                base_urgency = trait.adjust_urgency(base_urgency, t=t, state=state, goal=self)
        return base_urgency

    def utility(self, state: Dict) -> float:
        base_utility = self.utility_fn(state)
        for trait in self.traits:
            if hasattr(trait, 'adjust_utility'):
                base_utility = trait.adjust_utility(base_utility, state=state, goal=self)
        return base_utility

    def dependency_value(self, t: float, state: Dict) -> float:
        if not self.dependencies:
            return 0.0
        dep_values = [dep.effective_value(t, state) for dep in self.dependencies]
        return sum(dep_values) / len(dep_values)

    def base_effective_value(self, t: float, state: Dict) -> float:
        return self.urgency(t, state) * self.utility(state)

    def effective_value(self, t: float, state: Dict) -> float:
        base = self.base_effective_value(t, state)
        dep_bonus = self.dependency_value(t, state)

        modifier_sum = 0.0
        for trait in self.traits:
            modifier = trait.modify(
                base=base,
                urgency=self.urgency(t, state),
                utility=self.utility(state),
                dependencies=self.dependencies,
                dep_value=dep_bonus,
                state=state,
                goal=self,
                t=t
            )
            modifier_sum += modifier

        return base + dep_bonus + modifier_sum

    def describe(self, t: float, state: Dict) -> str:
        urgency_val = self.urgency(t, state)
        utility_val = self.utility(state)
        base = urgency_val * utility_val
        dep_bonus = self.dependency_value(t, state)
        final = self.effective_value(t, state)
        traits_list = ', '.join([trait.__class__.__name__ for trait in self.traits]) or 'None'

        return (
            f"Goal: {self.name}\n"
            f"  Traits: {traits_list}\n"
            f"  Urgency(t={t:.2f}): {urgency_val:.4f}\n"
            f"  Utility(state): {utility_val:.4f}\n"
            f"  Dependency Bonus: {dep_bonus:.4f}\n"
            f"  Base Value: {base:.4f}\n"
            f"  Total Effective Value: {final:.4f}"
        )


def linear_urgency(t: float) -> float:
    """Simple urgency decreases linearly from 1 to 0 over time."""
    return max(0.0, 1.0 - t)

def curiosity_utility(state: Dict) -> float:
    """Utility proportional to novelty measure in state."""
    return state.get('novelty', 0.5)

def safety_utility(state: Dict) -> float:
    """Utility proportional to safety level in state."""
    return state.get('safety_level', 1.0)

import math
from typing import Callable, Dict, List, Optional

from core.shared_types import Trait, TraitSet, URGENCY_SENSITIVE, RISK_AVERSE, EXPLORATORY

class Goal:
    def __init__(
        self,
        name: str,
        urgency_fn: Callable[[float], float],
        utility_fn: Callable[[Dict], float],
        dependencies: Optional[List['Goal']] = None,
        traits: Optional[TraitSet] = None
    ):
        self.name = name
        self.urgency_fn = urgency_fn
        self.utility_fn = utility_fn
        self.dependencies = dependencies or []

        if traits is None:
            self.traits = TraitSet([])
        elif isinstance(traits, TraitSet):
            self.traits = traits
        else:
            self.traits = TraitSet(traits)

    def urgency(self, t: float, state: Optional[Dict] = None) -> float:
        base = self.urgency_fn(t)

        if self.traits.has_trait(URGENCY_SENSITIVE):
            time_factor = 1.0 + 0.5 * (1.0 - base)
            base *= time_factor

        if self.traits.has_trait(RISK_AVERSE):
            risk = state.get("risk", 0.0) if state else 0.0
            base *= max(0.1, 1.0 - risk)

        return base

    def utility(self, state: Dict) -> float:
        base = self.utility_fn(state)

        if self.traits.has_trait(EXPLORATORY):
            novelty = state.get("novelty", 0.5)
            base *= 1.0 + 0.5 * novelty

        if self.traits.has_trait(RISK_AVERSE):
            safety = state.get("safety_level", 1.0)
            base *= safety

        return base

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

        trait_mod = 0.0

        if self.traits.has_trait(URGENCY_SENSITIVE):
            trait_mod += 0.1 * base

        if self.traits.has_trait(RISK_AVERSE):
            risk = state.get("risk", 0.0)
            trait_mod -= 0.2 * risk * base

        if self.traits.has_trait(EXPLORATORY):
            novelty = state.get("novelty", 0.5)
            trait_mod += 0.15 * novelty * base

        return base + dep_bonus + trait_mod

    def describe(self, t: float, state: Dict) -> str:
        urgency_val = self.urgency(t, state)
        utility_val = self.utility(state)
        base = urgency_val * utility_val
        dep_bonus = self.dependency_value(t, state)
        final = self.effective_value(t, state)

        # Defensive trait extraction
        traits_list = 'None'
        if hasattr(self.traits, 'traits') and self.traits.traits:
            traits_names = []
            for trait in self.traits.traits:
                name = getattr(trait, 'name', None)
                if name:
                    traits_names.append(name)
                else:
                    traits_names.append(str(trait))
            traits_list = ', '.join(traits_names)

        return (
            f"Goal: {self.name}\n"
            f"  Traits: {traits_list}\n"
            f"  Urgency(t={t:.2f}): {urgency_val:.4f}\n"
            f"  Utility(state): {utility_val:.4f}\n"
            f"  Dependency Bonus: {dep_bonus:.4f}\n"
            f"  Base Value: {base:.4f}\n"
            f"  Trait Modifiers: {final - (base + dep_bonus):.4f}\n"
            f"  Total Effective Value: {final:.4f}"
        )

# --- Sample Urgency and Utility Functions ---

def linear_urgency(t: float) -> float:
    return max(0.0, 1.0 - t)

def curiosity_utility(state: Dict) -> float:
    return state.get('novelty', 0.5)

def safety_utility(state: Dict) -> float:
    return state.get('safety_level', 1.0)

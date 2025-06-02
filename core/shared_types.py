from typing import Any, List

class Trait:
    def __init__(self, name: str, weight: float):
        self.name = name
        self.weight = weight

    def __repr__(self):
        return f"Trait(name={self.name}, weight={self.weight})"

# Predefined trait constants for shared usage
URGENCY_SENSITIVE = Trait("URGENCY_SENSITIVE", 1.0)
RISK_AVERSE = Trait("RISK_AVERSE", 1.0)
EXPLORATORY = Trait("EXPLORATORY", 1.0)

class TraitSet:
    def __init__(self, traits: List[Trait]):
        self.traits = {trait.name: trait for trait in traits}

    def get_weight(self, name: str) -> float:
        return self.traits.get(name, Trait(name, 0.0)).weight

    def has_trait(self, trait: Trait) -> bool:
        return trait.name in self.traits

    def __repr__(self):
        return f"TraitSet({list(self.traits.values())})"

class Goal:
    def __init__(self, name: str, urgency_fn, utility_fn):
        self.name = name
        self.urgency_fn = urgency_fn
        self.utility_fn = utility_fn

    def compute_urgency(self, state: Any) -> float:
        return self.urgency_fn(state)

    def compute_utility(self, state: Any) -> float:
        return self.utility_fn(state)

    def __repr__(self):
        return f"Goal(name={self.name})"

from typing import Optional, Iterable
from enum import Enum, auto

class Trait(Enum):
    URGENCY_SENSITIVE = auto()
    RISK_AVERSE = auto()
    EXPLORATORY = auto()
    DEPENDENCY_CRITICAL = auto()

class TraitSet:
    def __init__(self, traits: Optional[Iterable[Trait]] = None):
        # Immutable frozenset holds the traits
        self.traits: frozenset[Trait] = frozenset(traits) if traits else frozenset()

    def add_trait(self, trait: Trait) -> 'TraitSet':
        # Returns a new TraitSet with trait added (immutability preserved)
        return TraitSet(set(self.traits) | {trait})

    def remove_trait(self, trait: Trait) -> 'TraitSet':
        # Returns a new TraitSet with trait removed
        return TraitSet(set(self.traits) - {trait})

    def has_trait(self, trait: Trait) -> bool:
        return trait in self.traits

    def __repr__(self) -> str:
        trait_names = sorted(t.name for t in self.traits)
        return f"TraitSet({trait_names})"

    def __eq__(self, other) -> bool:
        return isinstance(other, TraitSet) and self.traits == other.traits

    def __hash__(self) -> int:
        return hash(self.traits)

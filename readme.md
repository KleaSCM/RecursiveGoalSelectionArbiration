# Goal Prioritization Engine

A mathematically-grounded goal prioritization engine, inspired by cognitive architectures and formalized in the accompanying paper: *"Mathematical Formalization of Consciousness Coupling and Attractor Collapse"* by Klea (May 2025). This engine models recursive, trait-modulated goal valuation with dependencies and dynamic traits such as risk aversion, urgency sensitivity, and exploratory tendencies.

## Overview

The system implements:

* **Goal representation**: Named, modular goal objects.
* **Urgency/Utility valuation**: Separately composable functions per goal.
* **Trait-sensitive modulation**: Dynamic adjustment of values based on psychological or cognitive traits.
* **Dependency-based bonus valuation**: Recursive evaluation of prerequisite goals.
* **Descriptive tracing**: Fully verbose breakdown of computed value components.

This modular architecture is simulation-ready and serves as a component within recursive cognitive systems (e.g. Shandris AGI). It is capable of Lyapunov-stable goal selection in multi-agent cognitive fields.

---

## Contents

* [Installation](#installation)
* [Usage](#usage)
* [Mathematical Foundation](#mathematical-foundation)
* [Goal Class Design](#goal-class-design)
* [Trait Set Architecture](#trait-set-architecture)
* [Urgency and Utility Functions](#urgency-and-utility-functions)
* [Effective Value Computation](#effective-value-computation)
* [Describe Output](#describe-output)
* [Example](#example)
* [License](#license)

---

## Installation

```bash
pip install -e .  # If part of a larger package
```

Ensure the following file structure exists:

```
project_root/
├── core/
│   └── shared_types.py
├── goals/
│   └── goal_model.py
├── tests/
└── README.md
```

### Dependencies

* Python 3.8+
* `math`, `typing` (standard)

Your `shared_types.py` must define:

```python
class Trait:
    def __init__(self, name: str):
        self.name = name

class TraitSet:
    def __init__(self, traits: List[Trait]):
        self.traits = traits

    def has_trait(self, trait: Trait) -> bool:
        return trait in self.traits

URGENCY_SENSITIVE = Trait("urgency-sensitive")
RISK_AVERSE = Trait("risk-averse")
EXPLORATORY = Trait("exploratory")
```

---

## Usage

```python
from goals.goal_model import Goal, describe, linear_urgency, curiosity_utility
from core.shared_types import URGENCY_SENSITIVE, TraitSet

exploration_goal = Goal(
    name="Explore New Region",
    urgency_fn=linear_urgency,
    utility_fn=curiosity_utility,
    traits=TraitSet([URGENCY_SENSITIVE])
)

state = {"novelty": 0.8, "risk": 0.1, "safety_level": 0.9}
print(describe(exploration_goal, t=0.5, state=state))
```

---

## Mathematical Foundation

Let:

* $U(t)$: urgency function
* $V(s)$: utility function with respect to state $s$
* $T$: trait set
* $D(t, s)$: mean value of dependencies

We define:

$$
\text{BaseValue}(t, s) = U(t) \cdot V(s)
$$

$$
\text{EffectiveValue}(t, s) = \text{BaseValue} + D(t, s) + M(t, s; T)
$$

Where modifier term $M$ is given by:

$$
M(t, s; T) =
  \alpha_1 \cdot 1_{\text{urgency-sensitive}} \cdot \text{BaseValue}
+ \alpha_2 \cdot 1_{\text{risk-averse}} \cdot (-\text{risk} \cdot \text{BaseValue})
+ \alpha_3 \cdot 1_{\text{exploratory}} \cdot \text{novelty} \cdot \text{BaseValue}
$$

---

## Goal Class Design

```python
class Goal:
    def __init__(
        name: str,
        urgency_fn: Callable[[float], float],
        utility_fn: Callable[[Dict], float],
        dependencies: Optional[List['Goal']] = None,
        traits: Optional[TraitSet] = None
    )
```

* `urgency_fn`: $U(t)$
* `utility_fn`: $V(s)$
* `traits`: trait-conditioned modifiers
* `dependencies`: optional prerequisite goals

### API:

* `urgency(t, state)`
* `utility(state)`
* `effective_value(t, state)`
* `describe(t, state)` (external)

---

## Trait Set Architecture

The `TraitSet` provides polymorphic modulation of values:

* `URGENCY_SENSITIVE`: boosts urgency
* `RISK_AVERSE`: suppresses value under risk
* `EXPLORATORY`: boosts value in novel states

All trait effects are formalized and weighted. Traits are designed to be extendable with modular influence models.

---

## Urgency and Utility Functions

These are plug-and-play functions. Examples:

```python
def linear_urgency(t):
    return max(0.0, 1.0 - t)

def curiosity_utility(state):
    return state.get("novelty", 0.5)

def safety_utility(state):
    return state.get("safety_level", 1.0)
```

---

## Effective Value Computation

```python
def effective_value(self, t: float, state: Dict) -> float:
    base = self.urgency(t, state) * self.utility(state)
    dep_bonus = self.dependency_value(t, state)
    trait_mod = compute_trait_modifiers(base, t, state)
    return base + dep_bonus + trait_mod
```

Includes:

* Linear urgency modulation
* Nonlinear trait weighting
* Mean dependency boost

---

## Describe Output

The `describe(goal, t, state)` method prints a detailed trace:

```text
Goal: Explore New Region
  Traits: urgency-sensitive
  Urgency(t=0.50): 0.5000
  Utility(state): 0.8000
  Dependency Bonus: 0.0000
  Base Value: 0.4000
  Trait Modifiers: 0.0200
  Total Effective Value: 0.4200
```

This is useful for debugging recursive goal states.

---

## Example

```python
G1 = Goal("Scout", linear_urgency, curiosity_utility, traits=TraitSet([EXPLORATORY]))
G2 = Goal("Secure Perimeter", linear_urgency, safety_utility, dependencies=[G1], traits=TraitSet([RISK_AVERSE]))

print(describe(G2, t=0.25, state={"risk": 0.2, "novelty": 0.9, "safety_level": 0.6}))
```

---

## License

MIT License. Use freely with attribution to Aikawa Yuriko and contributors.

---

## Citation

Klea. (2025). *Mathematical Formalization of Consciousness Coupling and Attractor Collapse*. Self-published manuscript, May 2025. Fitzroy Crossing, WA.

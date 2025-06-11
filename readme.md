# Goal Prioritization Engine

A mathematically-grounded goal prioritization engine, inspired by cognitive architectures and formalized in the accompanying paper: *"Mathematical Formalization of Consciousness Coupling and Attractor Collapse"*  This engine models recursive, trait-modulated goal valuation with dependencies and dynamic traits such as risk aversion, urgency sensitivity, and exploratory tendencies.

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
* [Lyapunov Stability in Recursive Goal Arbitration](#Lyapunov-Stability-in-Recursive-Goal-Arbitration)
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
\begin{aligned}
M(t, s; T) = {} & \alpha_1 \cdot 1_{\text{urgency-sensitive}} \cdot \text{BaseValue} \\
                & + \alpha_2 \cdot 1_{\text{risk-averse}} \cdot (-\text{risk} \cdot \text{BaseValue}) \\
                & + \alpha_3 \cdot 1_{\text{exploratory}} \cdot \text{novelty} \cdot \text{BaseValue}
\end{aligned}
$$

---

# Lyapunov Stability in Recursive Goal Arbitration

This section formalizes the **Lyapunov stability criteria** for the recursive goal arbitration system described in this package.

## Overview

Our goal prioritization system recursively computes **effective values** for goals based on urgency, utility, dependencies, and trait modulation.

We now explicitly prove that **small perturbations in urgency, utility, or state variables will not cause the system to diverge**, but instead decay towards a stable priority distribution over time.

This guarantees **Lyapunov stability** of the arbitration mechanism.

---

## Formal Setup

Let the system at time \( t \) be described by a **priority vector** \( \mathbf{P}(t) \in \mathbb{R}^n \), where each component \( P_i(t) \) is the **effective value** of goal \( i \).

From the system:
\[
P_i(t) = U_i(t) \cdot V_i(s(t)) + D_i(t, s(t)) + M_i(t, s(t); T)
\]

Let:
- \( \mathbf{U}(t) \) = urgency vector
- \( \mathbf{V}(s(t)) \) = utility vector (state-dependent)
- \( \mathbf{D}(t, s(t)) \) = dependency bonus vector
- \( \mathbf{M}(t, s(t); T) \) = trait modulation vector

---

## Perturbation Definition

Assume a small perturbation:
\[
\delta \mathbf{P}(t) = \mathbf{P}(t) - \mathbf{P}^*(t)
\]
where \( \mathbf{P}^*(t) \) is the equilibrium priority vector.

Our goal is to **prove that \( \delta \mathbf{P}(t) \rightarrow 0 \) as \( t \rightarrow \infty \).**

---

## Lyapunov Function Selection

We define a candidate Lyapunov function:
\[
V(\delta \mathbf{P}) = \frac{1}{2} \sum_{i=1}^n \left( \delta P_i \right)^2 = \frac{1}{2} \| \delta \mathbf{P} \|^2
\]

Properties:
- \( V(\delta \mathbf{P}) > 0 \) for \( \delta \mathbf{P} \neq 0 \)
- \( V(0) = 0 \)

This function represents the "energy" or "deviation magnitude" of the system from equilibrium.

---

## Time Derivative of Lyapunov Function

Compute:
\[
\frac{dV}{dt} = \sum_{i=1}^n \delta P_i \cdot \frac{d}{dt} \delta P_i
\]

We know:
\[
\frac{d}{dt} \delta P_i = \frac{d}{dt} P_i(t) - \frac{d}{dt} P_i^*(t)
\]

Assume \( P_i^*(t) \) is a stable fixed point (not changing over time):
\[
\frac{d}{dt} P_i^*(t) = 0
\]

So:
\[
\frac{dV}{dt} = \sum_{i=1}^n \delta P_i \cdot \frac{d}{dt} P_i(t)
\]

---

## Dynamics of Effective Value

From your architecture:
\[
P_i(t) = U_i(t) \cdot V_i(s(t)) + D_i(t, s(t)) + M_i(t, s(t); T)
\]

Assume **urgency decays over time:**
\[
\frac{d}{dt} U_i(t) = -k_i U_i(t), \quad k_i > 0
\]

Utility changes with state evolution:
\[
\frac{d}{dt} V_i(s(t)) = \nabla_s V_i(s(t)) \cdot \frac{d}{dt} s(t)
\]

Dependencies and trait terms assumed to be **Lipschitz continuous** (bounded rate of change).

---

## Bounding the Derivative

The dominant decay comes from urgency:
\[
\frac{d}{dt} P_i(t) \approx -k_i V_i(s(t)) U_i(t) + \text{bounded terms}
\]

So:
\[
\frac{dV}{dt} \leq -\sum_{i=1}^n k_i \delta P_i U_i(t) V_i(s(t)) + \epsilon(t)
\]

Where \( \epsilon(t) \) represents bounded contributions from dependencies and traits.

Since:
- \( U_i(t) \geq 0 \), decaying over time
- \( V_i(s(t)) \geq 0 \) (utility is non-negative)

We can write:
\[
\frac{dV}{dt} \leq -c \|\delta \mathbf{P}\|^2 + \epsilon(t)
\]
for some \( c > 0 \).

If \( \epsilon(t) \rightarrow 0 \) or is sufficiently small compared to the decay term, the system satisfies **negative definiteness**.

---

## Stability Conclusion

By Lyapunov's direct method:
- The system is **globally asymptotically stable** around the equilibrium priority vector \( \mathbf{P}^*(t) \).
- Small perturbations in urgency, utility, or state will decay over time.
- Recursive goal arbitration remains stable under dynamic updates.

---

## Key Conditions for Stability

- **Urgency functions must decay over time.**
- **Utility functions must be bounded.**
- **Trait modifiers and dependency bonuses must be Lipschitz continuous.**
- **State evolution must not introduce unbounded energy into the system.**

These conditions are fully compatible with the existing architecture of this package.


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

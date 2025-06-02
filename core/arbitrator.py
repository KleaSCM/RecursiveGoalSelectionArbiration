import math
from typing import List, Optional, Dict, Union
from core.goalModule import Goal


class GoalArbitrator:
    """
    Arbitrates among a set of goals using configurable strategies:
    - max: selects goal with maximum effective value
    - softmax: probabilistic selection based on softmax over values
    - nash: Nash equilibrium arbitration for exactly two goals
    - lyapunov: preference for goals with stable or improving value trajectories
    
    Supports traits-based arbitration via expected values and tracks value history for Lyapunov.
    """

    def __init__(
        self,
        goals: Optional[List[Goal]] = None,
        mode: str = 'softmax',
        temperature: float = 1.0,
        nash_iterations: int = 20,
        delta_t: float = 0.1
    ):
        self.goals: List[Goal] = goals if goals is not None else []
        self.mode = mode
        self.temperature = temperature
        self.nash_iterations = nash_iterations
        self._previous_values: Dict[str, float] = {}  # For Lyapunov tracking, keyed by goal.name
        self._delta_t = delta_t

    def softmax(self, values: List[float]) -> List[float]:
        if not values:
            return []
        max_val = max(values)
        exps = [math.exp((v - max_val) / self.temperature) for v in values]
        sum_exps = sum(exps)
        if sum_exps == 0:
            # Avoid division by zero — uniform distribution
            return [1.0 / len(values)] * len(values)
        return [e / sum_exps for e in exps]

    def select_goal(self, t: float, state: dict) -> Optional[Goal]:
        """
        Select a single goal to pursue based on current mode and state.

        Args:
            t: current time or timestep
            state: environment/internal state dict used by goals to compute value

        Returns:
            Selected Goal or None if no goals available.
        """
        if not self.goals:
            return None

        if self.mode == 'max':
            values = [g.effective_value(t, state) for g in self.goals]
            max_index = values.index(max(values))
            return self.goals[max_index]

        elif self.mode == 'softmax':
            values = [g.effective_value(t, state) for g in self.goals]
            probs = self.softmax(values)
            if not probs:
                return None
            # Choose goal with max probability (deterministic choice)
            max_index = probs.index(max(probs))
            return self.goals[max_index]

        elif self.mode == 'nash':
            # Nash equilibrium only for exactly two goals
            if len(self.goals) != 2:
                raise ValueError("Nash arbitration requires exactly two goals.")
            return self.nash_arbitrate(t, state)

        elif self.mode == 'lyapunov':
            return self.lyapunov_arbitrate(t, state)

        else:
            # Default fallback to max
            values = [g.effective_value(t, state) for g in self.goals]
            max_index = values.index(max(values))
            return self.goals[max_index]

    def select(self, expected_values: Dict[Goal, float]) -> Union[Goal, Dict[Goal, float], None]:
        """
        Select or return probability distribution over goals based on expected values.

        Args:
            expected_values: Dict mapping Goals to their expected value

        Returns:
            - If two goals, returns single selected goal via Nash arbitration
            - Otherwise returns dict of normalized probabilities per goal
            - None if empty input
        """
        if not expected_values:
            return None

        goals_list = list(expected_values.keys())
        values = list(expected_values.values())

        if len(expected_values) == 2:
            # Temporarily set goals and use Nash arbitrator
            self.goals = goals_list
            return self.nash_arbitrate(t=0.0, state={})

        # Softmax probabilities over expected values
        probs = self.softmax(values)
        total_prob = sum(probs)
        if total_prob == 0:
            probs = [1.0 / len(probs)] * len(probs)
            total_prob = 1.0
        normalized_probs = {g: p / total_prob for g, p in zip(goals_list, probs)}
        return normalized_probs

    def nash_arbitrate(self, t: float, state: dict) -> Optional[Goal]:
        """
        Nash equilibrium arbitration for exactly two goals using iterative best response.

        Args:
            t: Current time.
            state: Current environment/internal state.

        Returns:
            Selected Goal instance or None.
        """
        if len(self.goals) != 2:
            raise ValueError("Nash arbitration supports exactly two goals.")

        g1, g2 = self.goals

        ev_g1 = g1.effective_value(t, state)
        ev_g2 = g2.effective_value(t, state)

        # Payoff matrices representing engagement utilities:
        # Rows correspond to g1's action (0=not engage,1=engage)
        # Columns correspond to g2's action (0=not engage,1=engage)

        payoff_g1 = [
            [0, 0],                 # g1 not engage
            [ev_g1, ev_g1 + ev_g2] # g1 engage
        ]

        payoff_g2 = [
            [0, ev_g2],             # g2 not engage
            [0, ev_g2 + ev_g1]      # g2 engage
        ]

        # Initialize mixed strategy probabilities (engagement probabilities)
        p1, p2 = 0.5, 0.5

        for _ in range(self.nash_iterations):
            # Best response for g1 given p2
            util_engage_g1 = p2 * payoff_g1[1][1] + (1 - p2) * payoff_g1[1][0]
            util_not_engage_g1 = p2 * payoff_g1[0][1] + (1 - p2) * payoff_g1[0][0]
            if util_engage_g1 > util_not_engage_g1:
                p1_new = 1.0
            elif util_engage_g1 < util_not_engage_g1:
                p1_new = 0.0
            else:
                p1_new = p1

            # Best response for g2 given p1
            util_engage_g2 = p1 * payoff_g2[1][1] + (1 - p1) * payoff_g2[0][1]
            util_not_engage_g2 = p1 * payoff_g2[1][0] + (1 - p1) * payoff_g2[0][0]
            if util_engage_g2 > util_not_engage_g2:
                p2_new = 1.0
            elif util_engage_g2 < util_not_engage_g2:
                p2_new = 0.0
            else:
                p2_new = p2

            # Check for convergence
            if abs(p1 - p1_new) < 1e-4 and abs(p2 - p2_new) < 1e-4:
                break

            p1, p2 = p1_new, p2_new

        # Choose goal with higher engagement probability; tie-break by effective value
        if p1 > p2:
            return g1
        elif p2 > p1:
            return g2
        else:
            return g1 if ev_g1 >= ev_g2 else g2

    def lyapunov_arbitrate(self, t: float, state: dict) -> Optional[Goal]:
        """
        Lyapunov stability-based arbitration: prefers goals with stable or improving
        effective values, using previous values to estimate temporal derivative.

        Args:
            t: Current time.
            state: Current environment/internal state.

        Returns:
            Selected Goal instance or None.
        """
        if not self.goals:
            return None

        candidates = []

        for goal in self.goals:
            current_val = goal.effective_value(t, state)
            prev_val = self._previous_values.get(goal.name, current_val)

            # Estimate time derivative of value
            v_dot = (current_val - prev_val) / self._delta_t if self._delta_t > 0 else 0.0

            # Lyapunov score favors goals with positive or stable values
            # (If you want to favor stability, you could penalize large positive derivatives
            # to avoid overshoot; here we reward positive slopes.)
            penalty_weight = 1.0
            lyapunov_score = current_val + penalty_weight * max(0.0, v_dot)

            candidates.append((lyapunov_score, goal))

            # Update stored previous value for next iteration
            self._previous_values[goal.name] = current_val

        # Sort ascending by score to select goal with best Lyapunov stability
        candidates.sort(key=lambda x: x[0], reverse=True)
        return candidates[0][1] if candidates else None

    # Trait-based arbitration (example extension)
    def trait_based_selection(self, traits: Dict[str, float], t: float, state: dict) -> Optional[Goal]:
        """
        Selects goal based on trait affinity or compatibility.

        Args:
            traits: Dict of trait name -> trait value
            t: current time
            state: current state dict

        Returns:
            Selected Goal or None.
        """
        if not self.goals:
            return None

        # Example: weighted sum of goal traits vs provided traits
        best_score = -math.inf
        best_goal = None
        for goal in self.goals:
            score = 0.0
            for trait_name, trait_value in traits.items():
                goal_trait_value = goal.get_trait_value(trait_name)
                if goal_trait_value is not None:
                    score += trait_value * goal_trait_value
            # Optionally add effective value as part of score
            score += goal.effective_value(t, state)
            if score > best_score:
                best_score = score
                best_goal = goal

        return best_goal

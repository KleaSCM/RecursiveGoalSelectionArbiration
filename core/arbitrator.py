import math
from typing import List, Optional, Dict, Union
from core.goalModule import Goal


class GoalArbitrator:
    def __init__(self, goals=None, mode='softmax', temperature=1.0, nash_iterations=20):
        self.goals = goals if goals is not None else []
        self.mode = mode
        self.temperature = temperature
        self.nash_iterations = nash_iterations
        self._previous_values = {}
        self._delta_t = 0.1

    def softmax(self, values: List[float]) -> List[float]:
        if not values:
            return []
        max_val = max(values)
        exps = [math.exp((v - max_val) / self.temperature) for v in values]
        sum_exps = sum(exps)
        if sum_exps == 0:
            return [1.0 / len(values)] * len(values)
        return [e / sum_exps for e in exps]

    def select_goal(self, t: float, state: dict) -> Optional[Goal]:
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
            max_index = probs.index(max(probs))
            return self.goals[max_index]
        elif self.mode == 'nash' and len(self.goals) == 2:
            return self.nash_arbitrate(t, state)
        elif self.mode == 'lyapunov':
            return self.lyapunov_arbitrate(t, state)
        else:
            values = [g.effective_value(t, state) for g in self.goals]
            max_index = values.index(max(values))
            return self.goals[max_index]

    def select(self, expected_values: Dict[Goal, float]) -> Union[Goal, Dict[Goal, float], None]:
        if not expected_values:
            return None
        goals_list = list(expected_values.keys())
        values = list(expected_values.values())
        if len(expected_values) == 2:
            self.goals = goals_list
            return self.nash_arbitrate(t=0.0, state={})
        probs = self.softmax(values)
        total = sum(probs)
        if total == 0:
            probs = [1.0 / len(probs)] * len(probs)
            total = 1.0
        return {g: p / total for g, p in zip(goals_list, probs)}

    # ... keep the rest of your methods as is ...



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

        # Payoff matrix for g1: rows = g1 actions, cols = g2 actions
        payoff_g1 = [
            [0, 0],                  # g1 does not engage
            [ev_g1, ev_g1 + ev_g2]   # g1 engages
        ]

        # Payoff matrix for g2: rows = g1 actions, cols = g2 actions
        payoff_g2 = [
            [0, ev_g2],              # g2 does not engage
            [0, ev_g2 + ev_g1]       # g2 engages
        ]

        # Initialize mixed strategies (probability of engaging)
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

            if abs(p1 - p1_new) < 1e-4 and abs(p2 - p2_new) < 1e-4:
                break

            p1, p2 = p1_new, p2_new

        # Choose goal with higher engagement probability, break ties by effective value
        if p1 > p2:
            return g1
        elif p2 > p1:
            return g2
        else:
            return g1 if ev_g1 >= ev_g2 else g2

    def lyapunov_arbitrate(self, t: float, state: dict) -> Optional[Goal]:
        """
        Lyapunov stability-based arbitration: prefers goals with stable or improving effective values.

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

            # Approximate time derivative of value
            v_dot = (current_val - prev_val) / self._delta_t if self._delta_t > 0 else 0.0

            # Lyapunov score: value + penalty for positive derivative (favor stability)
            penalty_weight = 1.0
            lyapunov_score = current_val + penalty_weight * max(0.0, v_dot)

            candidates.append((lyapunov_score, goal))
            self._previous_values[goal.name] = current_val

        # Select the goal with the lowest Lyapunov score (prefer stable/improving)
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1] if candidates else None

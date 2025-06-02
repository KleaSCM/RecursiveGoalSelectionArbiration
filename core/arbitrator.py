import math
from typing import List, Optional
from core.goalModule import Goal  

class GoalArbitrator:
    def __init__(self, goals: List[Goal], temperature: float = 1.0, nash_iterations: int = 20):
        """
        Args:
            goals: List of Goal instances to arbitrate between
            temperature: Softmax temperature parameter; higher = more exploration
            nash_iterations: Number of iterations for Nash equilibrium solver (two-goal case)
        """
        self.goals = goals
        self.temperature = temperature
        self.nash_iterations = nash_iterations
        self._previous_values = {}  # Stores last effective value per goal for derivative estimate
        self._delta_t = 0.1         # Time step for derivative approximation

    def softmax(self, values: List[float]) -> List[float]:
        """Compute softmax probabilities for a list of values."""
        max_val = max(values)
        exps = [math.exp((v - max_val) / self.temperature) for v in values]
        sum_exps = sum(exps)
        return [e / sum_exps for e in exps]

    def select_goal(self, t: float, state: dict) -> Optional[Goal]:
        """
        Selects a goal based on softmax arbitration over effective values.

        Args:
            t: current time
            state: current environment/internal state dictionary

        Returns:
            The selected Goal instance, or None if no goals
        """
        if not self.goals:
            return None

        values = [g.effective_value(t, state) for g in self.goals]
        probs = self.softmax(values)

        max_index = probs.index(max(probs))
        return self.goals[max_index]

    def nash_arbitrate(self, t: float, state: dict) -> Optional[Goal]:
        """
        Implements Nash equilibrium arbitration for exactly two goals.
        Uses iterative best response dynamics to find mixed strategy equilibrium.

        Args:
            t: current time
            state: current environment/internal state dictionary

        Returns:
            The selected Goal instance, or None if arbitration is not possible
        """
        if len(self.goals) != 2:
            raise ValueError("Nash arbitration currently only supports exactly two goals.")

        g1, g2 = self.goals

        ev_g1 = g1.effective_value(t, state)
        ev_g2 = g2.effective_value(t, state)

        payoff_g1 = [
            [0, 0],          
            [ev_g1, ev_g1 + ev_g2]  
        ]
        payoff_g2 = [
            [0, ev_g2],          
            [0, ev_g2 + ev_g1]   
        ]

        p1 = 0.5
        p2 = 0.5

        for _ in range(self.nash_iterations):
            util_engage_g1 = p2 * payoff_g1[1][1] + (1 - p2) * payoff_g1[1][0]
            util_not_engage_g1 = p2 * payoff_g1[0][1] + (1 - p2) * payoff_g1[0][0]
            p1_new = 1.0 if util_engage_g1 > util_not_engage_g1 else 0.0 if util_engage_g1 < util_not_engage_g1 else p1

            util_engage_g2 = p1 * payoff_g2[1][1] + (1 - p1) * payoff_g2[0][1]
            util_not_engage_g2 = p1 * payoff_g2[1][0] + (1 - p1) * payoff_g2[0][0]
            p2_new = 1.0 if util_engage_g2 > util_not_engage_g2 else 0.0 if util_engage_g2 < util_not_engage_g2 else p2

            if abs(p1 - p1_new) < 1e-4 and abs(p2 - p2_new) < 1e-4:
                break

            p1, p2 = p1_new, p2_new

        if p1 > p2:
            return g1
        elif p2 > p1:
            return g2
        else:
            return g1 if ev_g1 >= ev_g2 else g2

    def lyapunov_arbitrate(self, t: float, state: dict) -> Optional[Goal]:
        """
        Lyapunov stability-based arbitration:
        Selects the goal with minimal Lyapunov score, approximated as
        effective value plus penalty on positive rate of change (derivative).

        Args:
            t: current time
            state: current environment/internal state dictionary

        Returns:
            The selected Goal instance, or None if no goals available
        """
        if not self.goals:
            return None

        candidates = []

        for goal in self.goals:
            current_val = goal.effective_value(t, state)
            prev_val = self._previous_values.get(goal.name, current_val)

            # Approximate time derivative of Lyapunov function V_dot
            v_dot = (current_val - prev_val) / self._delta_t if self._delta_t > 0 else 0

            penalty_weight = 1.0  # Adjust to tune sensitivity to instability
            lyapunov_score = current_val + penalty_weight * max(0.0, v_dot)

            candidates.append((lyapunov_score, goal))

            # Store current value for next iteration
            self._previous_values[goal.name] = current_val

        # Return the goal with the minimal Lyapunov score (lowest “energy” + most stable)
        candidates.sort(key=lambda x: x[0])
        return candidates[0][1] if candidates else None

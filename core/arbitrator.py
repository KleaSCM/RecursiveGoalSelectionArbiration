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

        # Choose the goal with the highest probability (or sample stochastically if preferred)
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

        # Get payoff matrix: rows = g1 actions, cols = g2 actions
        # For simplicity: Each goal can either "engage" (1) or "not engage" (0)
        # Payoffs are the effective values when chosen alone or combined
        # Here, define payoff matrices from each goal's perspective
        # Payoffs: 
        # - When only goal itself engages: effective_value(t, state)
        # - When both engage: sum of effective_values (could be weighted, here additive)
        # - When not engage: 0 payoff

        ev_g1 = g1.effective_value(t, state)
        ev_g2 = g2.effective_value(t, state)

        # Payoff matrices for each goal (rows: g1 action, cols: g2 action)
        # Actions: 0 = not engage, 1 = engage
        payoff_g1 = [
            [0, 0],          # g1 not engage
            [ev_g1, ev_g1 + ev_g2]  # g1 engage
        ]
        payoff_g2 = [
            [0, ev_g2],          # g2 not engage
            [0, ev_g2 + ev_g1]   # g2 engage
        ]

        # Initialize mixed strategies (probability of engaging) for each goal
        p1 = 0.5
        p2 = 0.5

        for _ in range(self.nash_iterations):
            # Best response for g1 given p2
            util_engage_g1 = p2 * payoff_g1[1][1] + (1 - p2) * payoff_g1[1][0]
            util_not_engage_g1 = p2 * payoff_g1[0][1] + (1 - p2) * payoff_g1[0][0]
            p1_new = 1.0 if util_engage_g1 > util_not_engage_g1 else 0.0 if util_engage_g1 < util_not_engage_g1 else p1

            # Best response for g2 given p1
            util_engage_g2 = p1 * payoff_g2[1][1] + (1 - p1) * payoff_g2[0][1]
            util_not_engage_g2 = p1 * payoff_g2[1][0] + (1 - p1) * payoff_g2[0][0]
            p2_new = 1.0 if util_engage_g2 > util_not_engage_g2 else 0.0 if util_engage_g2 < util_not_engage_g2 else p2

            # Check convergence
            if abs(p1 - p1_new) < 1e-4 and abs(p2 - p2_new) < 1e-4:
                break

            p1, p2 = p1_new, p2_new

        # Decide final goal choice based on mixed strategies (probabilities)
        # Here pick the goal with higher probability of engaging
        if p1 > p2:
            return g1
        elif p2 > p1:
            return g2
        else:
            # Tie or indifference: pick the one with higher effective value
            return g1 if ev_g1 >= ev_g2 else g2

    def lyapunov_arbitrate(self, t: float, state: dict) -> Optional[Goal]:
        """
        Placeholder for Lyapunov stability-based arbitration method.
        """
        raise NotImplementedError("Lyapunov arbitration is not yet implemented.")

import math
from typing import List, Optional
from core.goalModule import Goal  

class GoalArbitrator:
    def __init__(self, goals: List[Goal], temperature: float = 1.0):
        """
        Args:
            goals: List of Goal instances to arbitrate between
            temperature: Softmax temperature parameter; higher = more exploration
        """
        self.goals = goals
        self.temperature = temperature

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

    # Placeholder for future Nash equilibrium-based method
    def nash_arbitrate(self):
        raise NotImplementedError("Nash equilibrium arbitration is not yet implemented.")

    # Placeholder for future Lyapunov stability-based method
    def lyapunov_arbitrate(self):
        raise NotImplementedError("Lyapunov arbitration is not yet implemented.")

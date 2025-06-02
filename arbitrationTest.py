import unittest
from core.goalModule import Goal, linear_urgency, curiosity_utility, safety_utility
from core.arbitrator import GoalArbitrator

class TestGoalArbitrator(unittest.TestCase):

    def setUp(self):
        self.state = {"novelty": 0.8, "danger": 0.3}
        self.t = 5.0
        self.g1 = Goal("Explore", linear_urgency, curiosity_utility)
        self.g2 = Goal("Survive", linear_urgency, safety_utility)
        self.g3 = Goal("Idle", linear_urgency, lambda s: 0.1)

    def test_softmax_probabilities_sum_to_one(self):
        arb = GoalArbitrator([self.g1, self.g2, self.g3], temperature=1.0)
        values = [g.effective_value(self.t, self.state) for g in arb.goals]
        probs = arb.softmax(values)
        self.assertAlmostEqual(sum(probs), 1.0)

    def test_select_goal_returns_valid_goal(self):
        arb = GoalArbitrator([self.g1, self.g2, self.g3])
        selected = arb.select_goal(self.t, self.state)
        self.assertIn(selected, [self.g1, self.g2, self.g3])

    def test_select_goal_with_empty_list(self):
        arb = GoalArbitrator([])
        selected = arb.select_goal(self.t, self.state)
        self.assertIsNone(selected)

if __name__ == "__main__":
    unittest.main()

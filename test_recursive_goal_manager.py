import unittest
from core.goalModule import Goal
from core.arbitrator import GoalArbitrator

class TestGoalArbitrator(unittest.TestCase):

    def setUp(self):
        self.g1 = Goal('g1', urgency_fn=lambda t: 1.0, utility_fn=lambda state: 10)
        self.g2 = Goal('g2', urgency_fn=lambda t: 1.0, utility_fn=lambda state: 20)
        self.g3 = Goal('g3', urgency_fn=lambda t: 1.0, utility_fn=lambda state: 30)
        self.t = 0.0
        self.state = {}

    def test_softmax_probabilities_sum_to_one(self):
        arb = GoalArbitrator(mode='softmax', temperature=1.0)
        values = [g.effective_value(self.t, self.state) for g in [self.g1, self.g2, self.g3]]
        probs = arb.softmax(values)
        self.assertAlmostEqual(sum(probs), 1.0, places=5)

    def test_select_returns_probability_distribution_for_more_than_two_goals(self):
        arb = GoalArbitrator()
        expected_values = {g: g.effective_value(self.t, self.state) for g in [self.g1, self.g2, self.g3]}
        selected = arb.select(expected_values)
        self.assertIsInstance(selected, dict)
        self.assertTrue(all(goal in [self.g1, self.g2, self.g3] for goal in selected.keys()))
        self.assertAlmostEqual(sum(selected.values()), 1.0)

    def test_select_returns_single_goal_for_two_goals(self):
        arb = GoalArbitrator()
        expected_values = {g: g.effective_value(self.t, self.state) for g in [self.g1, self.g2]}
        selected = arb.select(expected_values)
        self.assertIn(selected, [self.g1, self.g2])
        self.assertIsInstance(selected, Goal)

    def test_select_goal_with_empty_dict_returns_none(self):
        arb = GoalArbitrator()
        selected = arb.select({})
        self.assertIsNone(selected)


if __name__ == "__main__":
    unittest.main()

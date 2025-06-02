import unittest
from core.goalModule import Goal, linear_urgency, curiosity_utility, safety_utility


class TestGoalSystem(unittest.TestCase):

    def setUp(self):
        self.state = {"novelty": 0.8, "danger": 0.3}
        self.t = 5.0

    def test_simple_goal(self):
        goal = Goal("TestGoal", linear_urgency, curiosity_utility)
        self.assertAlmostEqual(goal.urgency(self.t), 0.5)
        self.assertAlmostEqual(goal.utility(self.state), 1.6)
        ev = goal.effective_value(self.t, self.state)
        self.assertAlmostEqual(ev, 0.5 * 1.6 * 1.0)

    def test_dependency_sum(self):
        g1 = Goal("G1", linear_urgency, curiosity_utility)
        g2 = Goal("G2", linear_urgency, safety_utility)
        master = Goal("Master", linear_urgency, lambda s: 0.5, dependencies=[g1, g2])

        ev_master = master.effective_value(self.t, self.state)
        ev_g1 = g1.effective_value(self.t, self.state)
        ev_g2 = g2.effective_value(self.t, self.state)
        expected = master.urgency(self.t)*0.5*1.0 + ev_g1 + ev_g2
        self.assertAlmostEqual(ev_master, expected)

    def test_cycle_detection(self):
        g1 = Goal("G1", linear_urgency, curiosity_utility)
        g2 = Goal("G2", linear_urgency, safety_utility, dependencies=[g1])
        g1.dependencies.append(g2)  # introduce cycle G1 <-> G2

        ev = g1.effective_value(self.t, self.state)
        # Should not infinite loop, just return sum without double-counting
        self.assertTrue(ev > 0)

if __name__ == "__main__":
    unittest.main()

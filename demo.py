from core.goalModule import Goal, linear_urgency, curiosity_utility, safety_utility
from core.arbitrator import GoalArbitrator

# Setup a quick goal tree
explore = Goal("Explore", linear_urgency, curiosity_utility)
survive = Goal("Survive", linear_urgency, safety_utility)
master = Goal("MasterGoal", linear_urgency, lambda s: 0.5, dependencies=[explore, survive])

# Create arbitrator with all three goals (softmax arbitration demo)
arb = GoalArbitrator([master, explore, survive])

# Sample environment state at time t
state = {"novelty": 0.7, "danger": 0.2}
t = 6.0

# Softmax arbitration: pick best goal
best_goal_softmax = arb.select_goal(t, state)
print("== Softmax Arbitration Decision ==")
print(f"Selected Goal: {best_goal_softmax.name}")
print(best_goal_softmax.describe(t, state))

print("\n---\n")

# Now demo Nash arbitration with exactly two goals
arb_two = GoalArbitrator([explore, survive])

try:
    best_goal_nash = arb_two.nash_arbitrate(t, state)
    print("== Nash Arbitration Decision ==")
    print(f"Selected Goal: {best_goal_nash.name}")
    print(best_goal_nash.describe(t, state))
except ValueError as e:
    print(f"Nash arbitration error: {e}")

from core.goalModule import Goal, linear_urgency, curiosity_utility, safety_utility
from core.arbitrator import GoalArbitrator
from core.state import CognitiveState

import random

# === Define the Goal Tree ===
explore = Goal("Explore", linear_urgency, curiosity_utility)
survive = Goal("Survive", linear_urgency, safety_utility)
master = Goal("MasterGoal", linear_urgency, lambda s: 0.5, dependencies=[explore, survive])
all_goals = [master, explore, survive]

# === Recursive Execution Function ===
def execute_goal(goal: Goal, t: float, state: CognitiveState, arbitrator: GoalArbitrator, depth=0):
    indent = "  " * depth
    print(f"{indent}→ Selected: {goal.name}")
    print(f"{indent}{goal.describe(t, state._state_data).replace(chr(10), chr(10) + indent)}")

    if goal.dependencies:
        print(f"{indent}↳ Resolving dependencies of {goal.name}...")
        subgoals = [g for g in arbitrator.goals if g.name in [d.name for d in goal.dependencies]]
        sub_arbitrator = GoalArbitrator(subgoals)
        selected_subgoal = sub_arbitrator.select_goal(t, state._state_data)
        if selected_subgoal:
            execute_goal(selected_subgoal, t, state, sub_arbitrator, depth + 1)
    else:
        print(f"{indent}✓ Executing leaf goal: {goal.name}")

# === Simulated Environment Dynamics ===
def update_state(state: CognitiveState, step: int):
    # Read current state variables
    novelty = state.get("novelty", 0.0)
    danger = state.get("danger", 0.0)

    # Simulate novelty decay and random danger fluctuation
    novelty = max(0.0, min(1.0, novelty * 0.95 + random.uniform(-0.05, 0.1)))
    danger = max(0.0, min(1.0, danger + random.uniform(-0.1, 0.1)))

    # Update state object
    state.set("novelty", novelty)
    state.set("danger", danger)

# === Main Demo Loop ===
def run_full_demo():
    state = CognitiveState()
    state.set("novelty", 0.7)
    state.set("danger", 0.2)
    t = 0.0
    arbitrator = GoalArbitrator(all_goals)

    print("===== FULL RECURSIVE GOAL SELECTION & EXECUTION DEMO =====")

    for step in range(5):
        print(f"\n\n=== Time Step {step} (t = {t:.1f}) ===")
        print(f"State: {state._state_data}")

        selected_goal = arbitrator.select_goal(t, state._state_data)
        if selected_goal:
            execute_goal(selected_goal, t, state, arbitrator)
        else:
            print("No goal selected.")

        update_state(state, step)
        t += 1.0

# === Run Nash Arbitration as separate showcase ===
def run_nash_demo():
    arb_two = GoalArbitrator([explore, survive])
    state = CognitiveState()
    state.set("novelty", 0.7)
    state.set("danger", 0.2)
    t = 6.0

    try:
        print("\n\n===== NASH ARBITRATION DEMO =====")
        best_goal_nash = arb_two.nash_arbitrate(t, state._state_data)
        print(f"Selected Goal: {best_goal_nash.name}")
        print(best_goal_nash.describe(t, state._state_data))
    except ValueError as e:
        print(f"Nash arbitration error: {e}")

# === Entry point ===
if __name__ == "__main__":
    run_full_demo()
    run_nash_demo()

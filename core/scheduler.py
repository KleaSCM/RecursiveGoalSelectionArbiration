import time
from goalModule import example_goal_tree

def run_scheduler(ticks=10, delay=0.5):
    state = {"novelty": 0.8, "danger": 0.3}
    master_goal = example_goal_tree()
    goals = [master_goal] + master_goal.dependencies

    print("Initial goals:")
    for g in goals:
        print(f"  - {g.name} (urgency={g.urgency(0):.2f}, utility={g.utility(state):.2f})")

    for t in range(ticks):
        print(f"\n--- Tick {t} ---")
        sorted_goals = sorted(
            goals,
            key=lambda g: g.effective_value(t, state),
            reverse=True
        )
        top = sorted_goals[0]

        for g in sorted_goals:
            print(f"{g.name}: urgency={g.urgency(t):.2f}, utility={g.utility(state):.2f}, "
                  f"eff={g.effective_value(t, state):.2f}")

        print(f"Selected Goal: {top.name}  ← Highest EV")

        time.sleep(delay)

if __name__ == "__main__":
    run_scheduler(ticks=20)

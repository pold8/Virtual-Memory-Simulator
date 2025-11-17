from simulator.simulation_engine import SimulationEngine
from simulator.replacement_policies.fifo import FIFOAlgorithm
from simulator.replacement_policies.lru import LRUAlgorithm
from simulator.replacement_policies.optimal import OptimalAlgorithm


def run_policy(policy, reference_string, num_frames):
    print(f"\n=== {policy.__class__.__name__} ===")
    engine = SimulationEngine(num_frames, reference_string, policy)

    while not engine.has_finished():
        step = engine.step()
        print(
            f"Step {step.step_index:02d} | page {step.requested_page} | "
            f"{'HIT ' if step.hit else 'FAULT'} | "
            f"frames = {step.frames_snapshot} "
            f"{'(evicted ' + str(step.evicted_page) + ')' if step.evicted_page is not None else ''}"
        )


def main():
    reference_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
    num_frames = 3

    policies = [
        FIFOAlgorithm(),
        LRUAlgorithm(),
        OptimalAlgorithm(),
    ]

    for policy in policies:
        run_policy(policy, reference_string, num_frames)


if __name__ == "__main__":
    main()

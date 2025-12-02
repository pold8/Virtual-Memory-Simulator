# main.py

from simulator.simulation_controller import SimulationController
from simulator.replacement_policies.fifo import FIFOAlgorithm
from simulator.replacement_policies.lru import LRUAlgorithm
from simulator.replacement_policies.optimal import OptimalAlgorithm


def run_policy(name, policy, reference_string, num_frames):
    print(f"\n=== Running {name} ===")
    controller = SimulationController(num_frames, reference_string, policy)

    while not controller.is_finished():
        step = controller.step()
        print(
            f"Step {step.step_index:02d} | page {step.requested_page} | "
            f"{'HIT ' if step.hit else 'FAULT'} | frames = {step.frames_snapshot} "
            f"{'(evicted ' + str(step.evicted_page) + ')' if step.evicted_page else ''}"
        )

    print("\n--- Statistics ---")
    print(f"Total accesses: {controller.stats.total_accesses}")
    print(f"Hits:           {controller.stats.hits}")
    print(f"Faults:         {controller.stats.faults}")
    print(f"Hit ratio:      {controller.stats.hit_ratio:.3f}")
    print(f"Fault ratio:    {controller.stats.fault_ratio:.3f}")


def main():
    reference_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
    num_frames = 3

    policies = [
        ("FIFO", FIFOAlgorithm()),
        ("LRU", LRUAlgorithm()),
        ("Optimal", OptimalAlgorithm()),
    ]

    for name, policy in policies:
        run_policy(name, policy, reference_string, num_frames)


if __name__ == "__main__":
    main()

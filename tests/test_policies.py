from simulator.replacement_policies.fifo import FIFOAlgorithm
from simulator.replacement_policies.lru import LRUAlgorithm
from simulator.replacement_policies.optimal import OptimalAlgorithm


def run_simulation(policy, reference_string, num_frames: int):
    frames = [None] * num_frames
    hits = 0
    faults = 0

    print(f"\n=== Testing {policy.__class__.__name__} ===")
    print(f"Frames: {num_frames}")
    print(f"Reference string: {reference_string}\n")

    for i, page in enumerate(reference_string):
        print(f"Step {i:02d}: request page {page}")

        if page in frames:
            hits += 1
            print(f"  -> HIT (frames: {frames})")
            continue

        faults += 1

        if None in frames:
            free_index = frames.index(None)
            frames[free_index] = page
            print(f"  -> FAULT, loaded into free frame {free_index} (frames: {frames})")
        else:
            # Memory full: ask policy which frame to evict
            victim_index = policy.select_victim(frames, reference_string, i)
            evicted = frames[victim_index]
            frames[victim_index] = page
            print(
                f"  -> FAULT, evict page {evicted} from frame {victim_index}, "
                f"load page {page} (frames: {frames})"
            )

    print(f"\nResult for {policy.__class__.__name__}:")
    print(f"  Hits:   {hits}")
    print(f"  Faults: {faults}")
    print(f"  Hit ratio:  {hits / len(reference_string):.3f}")
    print(f"  Fault ratio:{faults / len(reference_string):.3f}")
    print("-" * 40)


if __name__ == "__main__":
    reference_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
    num_frames = 3

    policies = [
        FIFOAlgorithm(),
        LRUAlgorithm(),
        OptimalAlgorithm(),
    ]

    for p in policies:
        run_simulation(p, reference_string, num_frames)

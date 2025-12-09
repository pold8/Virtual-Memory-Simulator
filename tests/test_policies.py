import unittest
from simulator.replacement_policies.fifo import FIFOAlgorithm
from simulator.replacement_policies.lru import LRUAlgorithm
from simulator.replacement_policies.optimal import OptimalAlgorithm

class TestPolicies(unittest.TestCase):
    def run_policy(self, policy, reference_string, num_frames):
        frames = [None] * num_frames
        hits = 0
        faults = 0

        for i, page in enumerate(reference_string):
            if page in frames:
                hits += 1
            else:
                faults += 1
                if None in frames:
                    free_index = frames.index(None)
                    frames[free_index] = page
                else:
                    victim_index = policy.select_victim(frames, reference_string, i)
                    frames[victim_index] = page
        return hits, faults

    def test_fifo(self):
        reference_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
        hits, faults = self.run_policy(FIFOAlgorithm(), reference_string, 3)
        self.assertEqual(hits, 3)
        self.assertEqual(faults, 10)

    def test_lru(self):
        reference_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
        hits, faults = self.run_policy(LRUAlgorithm(), reference_string, 3)
        self.assertEqual(hits, 4)
        self.assertEqual(faults, 9)

    def test_optimal(self):
        reference_string = [7, 0, 1, 2, 0, 3, 0, 4, 2, 3, 0, 3, 2]
        hits, faults = self.run_policy(OptimalAlgorithm(), reference_string, 3)
        self.assertEqual(hits, 6)
        self.assertEqual(faults, 7)

if __name__ == "__main__":
    unittest.main()

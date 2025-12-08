import unittest
from simulator.vm_config import VMConfig
from simulator.simulation_engine import SimulationEngine
from simulator.replacement_policies.fifo import FIFOAlgorithm

class TestSimulationEngine(unittest.TestCase):
    def setUp(self):
        # Small config: 16 bytes/page, 4 frames
        self.config = VMConfig(
             virtual_memory_size=256,
             physical_memory_size=64,
             offset_bits=4
        )
        self.policy = FIFOAlgorithm()
        # Pages: 0, 1, 2...
        # Page size 16. Address 0->Page0, 16->Page1
        self.ref_string = [
            (0, "R"),   # Page 0
            (16, "R"),  # Page 1
            (0, "W"),   # Page 0 (Hit)
            (32, "R"),  # Page 2
            (48, "R"),  # Page 3 (Full)
            (64, "R"),  # Page 4 (Evict Page 0? FIFO says yes)
        ]
        self.engine = SimulationEngine(
            vm_config=self.config,
            reference_string=self.ref_string,
            policy=self.policy,
            tlb_entries=2
        )

    def test_step_execution(self):
        # Step 0: Load Page 0
        res = self.engine.step()
        self.assertEqual(res.page, 0)
        self.assertFalse(res.hit) # Cold miss
        self.assertEqual(res.frame_index, 0)

        # Step 1: Load Page 1
        res = self.engine.step()
        self.assertEqual(res.page, 1)
        self.assertEqual(res.frame_index, 1)

        # Step 2: Write Page 0 (Present)
        res = self.engine.step()
        self.assertEqual(res.page, 0)
        self.assertTrue(res.hit)
        # Should set dirty bit internal check
        pte = self.engine.page_table.get(0)
        self.assertTrue(pte.dirty)

    def test_eviction_FIFO(self):
        # Run until memory full
        # 0, 1, 0, 2, 3
        # Frames at step 4 (after 3 loaded): [P0, P1, P2, P3] (FIFO order: 0, 1, 2, 3)
        
        for _ in range(5):
            self.engine.step()
        
        # Current frames: [0, 1, 2, 3] (indices)
        
        # Step 5: Load Page 4 (Address 64)
        # Should evict Page 0 (Frame 0)
        res = self.engine.step()
        self.assertEqual(res.page, 4)
        self.assertFalse(res.hit)
        self.assertTrue(res.fault)
        self.assertEqual(res.evicted_page, 0)
        self.assertEqual(res.victim_frame_index, 0)
        self.assertTrue(res.write_back) # Page 0 was dirty from Step 2

    def test_tlb_usage(self):
        # Step 0: Page 0 -> TLB Insert
        res = self.engine.step()
        self.assertFalse(res.tlb_hit)
        
        # Step 1: Page 1 -> TLB Insert (TLB: 0, 1)
        self.engine.step()

        # Step 2: Page 0 -> TLB Hit
        res = self.engine.step()
        self.assertTrue(res.tlb_hit)

if __name__ == "__main__":
    unittest.main()

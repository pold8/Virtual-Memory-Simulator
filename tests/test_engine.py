import unittest
from simulator.vm_config import VMConfig
from simulator.simulation_engine import SimulationEngine
from simulator.replacement_policies.fifo import FIFOAlgorithm

class TestSimulationEngine(unittest.TestCase):
    def setUp(self):
        self.config = VMConfig(
             virtual_memory_size=256,
             physical_memory_size=64,
             offset_bits=4
        )
        self.policy = FIFOAlgorithm()
        self.ref_string = [
            (0, "R"),   # Page 0
            (16, "R"),  # Page 1
            (0, "W"),   # Page 0 (Hit)
            (32, "R"),  # Page 2
            (48, "R"),  # Page 3 (Full)
            (64, "R"),  # Page 4
        ]
        self.engine = SimulationEngine(
            vm_config=self.config,
            reference_string=self.ref_string,
            policy=self.policy,
            tlb_entries=2
        )

    def test_step_execution(self):
        res = self.engine.step()
        self.assertEqual(res.page, 0)
        self.assertFalse(res.hit)
        self.assertEqual(res.frame_index, 0)

        res = self.engine.step()
        self.assertEqual(res.page, 1)
        self.assertEqual(res.frame_index, 1)

        res = self.engine.step()
        self.assertEqual(res.page, 0)
        self.assertTrue(res.hit)
        pte = self.engine.page_table.get(0)
        self.assertTrue(pte.dirty)

    def test_eviction_FIFO(self):
        
        for _ in range(5):
            self.engine.step()
        
        
        res = self.engine.step()
        self.assertEqual(res.page, 4)
        self.assertFalse(res.hit)
        self.assertTrue(res.fault)
        self.assertEqual(res.evicted_page, 0)
        self.assertEqual(res.victim_frame_index, 0)
        self.assertTrue(res.write_back)

    def test_tlb_usage(self):
        res = self.engine.step()
        self.assertFalse(res.tlb_hit)
        
        self.engine.step()

        res = self.engine.step()
        self.assertTrue(res.tlb_hit)

if __name__ == "__main__":
    unittest.main()

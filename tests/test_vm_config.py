import unittest
from simulator.vm_config import VMConfig

class TestVMConfig(unittest.TestCase):
    def test_initialization_small(self):
        config = VMConfig(
            virtual_memory_size=256,
            physical_memory_size=64,
            offset_bits=4
        )
        self.assertEqual(config.page_size, 16)
        self.assertEqual(config.num_frames, 4)
        self.assertEqual(config.num_virtual_pages, 16)

    def test_initialization_standard(self):
        config = VMConfig(
            virtual_memory_size=65536,
            physical_memory_size=4096,
            offset_bits=8
        )
        self.assertEqual(config.page_size, 256)
        self.assertEqual(config.num_frames, 16)
        self.assertEqual(config.num_virtual_pages, 256)

if __name__ == "__main__":
    unittest.main()

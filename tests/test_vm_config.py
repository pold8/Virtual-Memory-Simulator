import unittest
from simulator.vm_config import VMConfig

class TestVMConfig(unittest.TestCase):
    def test_initialization_small(self):
        # 256 bytes memory, 64 bytes physical, 4 bits offset (16 bytes page)
        # page_size = 16
        # num_frames = 64 / 16 = 4
        # num_pages = 256 / 16 = 16
        config = VMConfig(
            virtual_memory_size=256,
            physical_memory_size=64,
            offset_bits=4
        )
        self.assertEqual(config.page_size, 16)
        self.assertEqual(config.num_frames, 4)
        self.assertEqual(config.num_virtual_pages, 16)

    def test_initialization_standard(self):
        # 64 KB VM, 4 KB PM, 8 bits offset (256 bytes page)
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

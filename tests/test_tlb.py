import unittest
from simulator.tlb import TLB

class TestTLB(unittest.TestCase):
    def setUp(self):
        self.tlb = TLB(size=3)

    def test_insert_and_lookup(self):
        # Insert page 1 -> frame 10 at step 1
        self.tlb.insert(page=1, frame=10, current_step=1)
        
        # Lookup should hit
        frame = self.tlb.lookup(page=1, current_step=2)
        self.assertEqual(frame, 10)

        # Lookup unknown should fail
        frame = self.tlb.lookup(page=2, current_step=2)
        self.assertIsNone(frame)

    def test_lru_replacement(self):
        # Fill TLB (size 3)
        self.tlb.insert(1, 10, current_step=1)
        self.tlb.insert(2, 20, current_step=2)
        self.tlb.insert(3, 30, current_step=3)

        # 1 is oldest (timestamp 1). 
        # Access 1 to update timestamp? No, let's just insert 4.
        # Should evict 1.
        self.tlb.insert(4, 40, current_step=4)

        self.assertIsNone(self.tlb.lookup(1, 5))
        self.assertEqual(self.tlb.lookup(2, 5), 20)
        self.assertEqual(self.tlb.lookup(3, 5), 30)
        self.assertEqual(self.tlb.lookup(4, 5), 40)

    def test_update_existing(self):
        self.tlb.insert(1, 10, current_step=1)
        # Update frame for page 1
        self.tlb.insert(1, 99, current_step=2)
        
        self.assertEqual(self.tlb.lookup(1, 3), 99)
        self.assertEqual(len(self.tlb.entries), 1)

    def test_lookup_updates_access_time(self):
        self.tlb.insert(1, 10, current_step=1)
        self.tlb.insert(2, 20, current_step=2)
        self.tlb.insert(3, 30, current_step=3)

        # Access 1 at step 4 (making it newest)
        self.tlb.lookup(1, current_step=4)

        # Insert 4 at step 5. 
        # LRU should be 2 (timestamp 2), since 1 was just used.
        self.tlb.insert(4, 40, current_step=5)

        self.assertIsNotNone(self.tlb.lookup(1, 6)) # Should still be there
        self.assertIsNone(self.tlb.lookup(2, 6))    # Should be evicted
        self.assertIsNotNone(self.tlb.lookup(3, 6))
        self.assertIsNotNone(self.tlb.lookup(4, 6))

if __name__ == "__main__":
    unittest.main()

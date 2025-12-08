import unittest
from simulator.page_table import PageTable

class TestPageTable(unittest.TestCase):
    def setUp(self):
        self.pt = PageTable()

    def test_get_or_create_new(self):
        # Should create a new entry
        pte = self.pt.get_or_create(10)
        self.assertEqual(pte.page, 10)
        self.assertFalse(pte.present)
        self.assertFalse(pte.referenced)
        self.assertFalse(pte.dirty)
        self.assertIsNone(pte.frame_index)

    def test_get_existing(self):
        pte1 = self.pt.get_or_create(5)
        pte1.present = True
        
        pte2 = self.pt.get(5)
        self.assertEqual(pte1, pte2)
        self.assertTrue(pte2.present)

    def test_get_non_existent(self):
        pte = self.pt.get(999)
        self.assertIsNone(pte)

    def test_all_entries(self):
        self.pt.get_or_create(1)
        self.pt.get_or_create(2)
        entries = self.pt.all_entries()
        self.assertEqual(len(entries), 2)
        self.assertIn(1, entries)
        self.assertIn(2, entries)

if __name__ == "__main__":
    unittest.main()

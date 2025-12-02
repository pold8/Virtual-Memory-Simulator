from dataclasses import dataclass
from typing import Optional, Dict


@dataclass
class TLBEntry:
    page: int
    frame: int
    last_access: int


class TLB:

    def __init__(self, size: int):
        self.size = size
        self.entries: Dict[int, TLBEntry] = {}

    def lookup(self, page: int, current_step: int) -> Optional[int]:
        """Return frame number if TLB hit, else None."""
        if page in self.entries:
            self.entries[page].last_access = current_step
            return self.entries[page].frame
        return None

    def insert(self, page: int, frame: int, current_step: int):
        """Insert or update a TLB entry using LRU replacement."""
        # Case 1: Already in TLB
        if page in self.entries:
            self.entries[page].frame = frame
            self.entries[page].last_access = current_step
            return

        # Case 2: Free space
        if len(self.entries) < self.size:
            self.entries[page] = TLBEntry(page, frame, current_step)
            return

        # Case 3: LRU replacement
        lru_page = min(self.entries.values(), key=lambda e: e.last_access).page
        del self.entries[lru_page]
        self.entries[page] = TLBEntry(page, frame, current_step)

from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class PageTableEntry:
    """Simplified page table entry."""
    page: int
    frame_index: Optional[int] = None   # index of the frame holding this page
    present: bool = False               # is the page currently in RAM?
    referenced: bool = False            # gets set on access
    dirty: bool = False                 # not really used yet


class PageTable:
    """Maps virtual pages to PageTableEntry objects."""

    def __init__(self) -> None:
        self._entries: Dict[int, PageTableEntry] = {}

    def get_or_create(self, page: int) -> PageTableEntry:
        if page not in self._entries:
            self._entries[page] = PageTableEntry(page=page)
        return self._entries[page]

    def get(self, page: int) -> Optional[PageTableEntry]:
        return self._entries.get(page)

    def all_entries(self) -> Dict[int, PageTableEntry]:
        """Useful later for showing the whole page table in the UI."""
        return dict(self._entries)

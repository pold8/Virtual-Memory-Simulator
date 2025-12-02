from __future__ import annotations
from dataclasses import dataclass
from typing import Dict, Optional


@dataclass
class PageTableEntry:
    page: int
    frame_index: Optional[int] = None
    present: bool = False
    referenced: bool = False
    dirty: bool = False


class PageTable:

    def __init__(self) -> None:
        self._entries: Dict[int, PageTableEntry] = {}

    def get_or_create(self, page: int) -> PageTableEntry:
        if page not in self._entries:
            self._entries[page] = PageTableEntry(page=page)
        return self._entries[page]

    def get(self, page: int) -> Optional[PageTableEntry]:
        return self._entries.get(page)

    def all_entries(self) -> Dict[int, PageTableEntry]:
        return dict(self._entries)

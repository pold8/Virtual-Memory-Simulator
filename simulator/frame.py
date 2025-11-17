from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Frame:
    """Represents a physical memory frame."""
    index: int
    page: Optional[int] = None          # current page number in this frame
    loaded_time: int = -1               # step when the page was loaded
    last_access_time: int = -1          # step of last access

    @property
    def is_free(self) -> bool:
        return self.page is None

from __future__ import annotations
from dataclasses import dataclass
from typing import Optional


@dataclass
class Frame:
    index: int
    page: Optional[int] = None
    loaded_time: int = -1
    last_access_time: int = -1

    @property
    def is_free(self) -> bool:
        return self.page is None

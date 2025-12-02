from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Optional


class ReplacementPolicy(ABC):
    @abstractmethod
    def select_victim(
        self,
        frames: list[Optional[int]],
        reference_string: list[int],
        current_index: int,
    ) -> int:
        raise NotImplementedError

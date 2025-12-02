from __future__ import annotations

from collections import deque
from typing import Optional, List

from simulator.base_policy import ReplacementPolicy


class FIFOAlgorithm(ReplacementPolicy):

    def __init__(self) -> None:
        # Queue of frame indices, left = oldest, right = newest
        self._order: deque[int] = deque()

    def _ensure_initialized(self, frames: List[Optional[int]]) -> None:
        if not self._order and all(f is not None for f in frames):
            self._order = deque(range(len(frames)))

    def select_victim(
        self,
        frames: list[Optional[int]],
        reference_string: list[int],
        current_index: int,
    ) -> int:
        self._ensure_initialized(frames)

        if not self._order:
            return 0

        victim = self._order.popleft()
        self._order.append(victim)
        return victim

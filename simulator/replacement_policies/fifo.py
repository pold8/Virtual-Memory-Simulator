from __future__ import annotations

from collections import deque
from typing import Optional, List

from simulator.base_policy import ReplacementPolicy


class FIFOAlgorithm(ReplacementPolicy):
    """
    First-In, First-Out replacement.
    We track the order in which frame slots were filled and always evict
    the one that has been in memory the longest.
    """

    def __init__(self) -> None:
        # Queue of frame indices, left = oldest, right = newest
        self._order: deque[int] = deque()

    def _ensure_initialized(self, frames: List[Optional[int]]) -> None:
        """
        Lazily initialize the queue when we know the number of frames.
        Assumes frames are initially filled from index 0..n-1 in order.
        """
        if not self._order and all(f is not None for f in frames):
            self._order = deque(range(len(frames)))

    def select_victim(
        self,
        frames: list[Optional[int]],
        reference_string: list[int],
        current_index: int,
    ) -> int:
        # Make sure we have an order queue
        self._ensure_initialized(frames)

        if not self._order:
            # Fallback: just evict frame 0
            return 0

        victim = self._order.popleft()
        # After we replace this frame, its "new" page is the most recent
        self._order.append(victim)
        return victim

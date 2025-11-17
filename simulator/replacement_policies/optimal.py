from __future__ import annotations
from typing import Optional

from simulator.base_policy import ReplacementPolicy


class OptimalAlgorithm(ReplacementPolicy):
    """
    Optimal (MIN) replacement.
    Evicts the page whose *next* use is farthest in the future.
    If a page is never used again, it is chosen immediately.
    """

    def select_victim(
        self,
        frames: list[Optional[int]],
        reference_string: list[int],
        current_index: int,
    ) -> int:
        """
        :param frames: list of current page numbers in frames (no Nones, memory is full)
        :param reference_string: full sequence of page references
        :param current_index: index in reference_string of the *current* faulting access
        :return: index of frame to evict
        """
        victim_frame = 0
        farthest_next_use = -1  # how far in the future its next use is

        for frame_index, page in enumerate(frames):
            if page is None:
                # Empty frame shouldn't happen here, but just in case
                return frame_index

            # Look ahead to find the next time this page is used
            next_use_index = -1
            for i in range(current_index + 1, len(reference_string)):
                if reference_string[i] == page:
                    next_use_index = i
                    break

            if next_use_index == -1:
                # Page is never used again -> perfect victim
                return frame_index

            distance = next_use_index - current_index
            if distance > farthest_next_use:
                farthest_next_use = distance
                victim_frame = frame_index

        return victim_frame

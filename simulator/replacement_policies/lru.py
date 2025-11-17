from __future__ import annotations
from typing import Optional

from simulator.base_policy import ReplacementPolicy


class LRUAlgorithm(ReplacementPolicy):
    """
    Least Recently Used replacement.
    We choose the frame whose page was used farthest in the past.
    This implementation recomputes "last use" from the reference string
    each time select_victim is called (fine for an educational simulator).
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
        # Index of frame whose page was least recently used
        victim_frame = 0
        oldest_distance = -1  # how many steps ago it was last used

        for frame_index, page in enumerate(frames):
            if page is None:
                # Shouldn't happen when memory is full, but be safe
                return frame_index

            # Search backwards to find the last time this page was referenced
            last_use_index = -1
            for i in range(current_index - 1, -1, -1):
                if reference_string[i] == page:
                    last_use_index = i
                    break

            if last_use_index == -1:
                # Page was never used before -> it's the best victim
                return frame_index

            distance = current_index - last_use_index

            if distance > oldest_distance:
                oldest_distance = distance
                victim_frame = frame_index

        return victim_frame

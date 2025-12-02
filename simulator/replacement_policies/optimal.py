from __future__ import annotations
from typing import Optional

from simulator.base_policy import ReplacementPolicy


class OptimalAlgorithm(ReplacementPolicy):

    def select_victim(
        self,
        frames: list[Optional[int]],
        reference_string: list[int],
        current_index: int,
    ) -> int:
        victim_frame = 0
        farthest_next_use = -1

        for frame_index, page in enumerate(frames):
            if page is None:
                return frame_index

            next_use_index = -1
            for i in range(current_index + 1, len(reference_string)):
                if reference_string[i] == page:
                    next_use_index = i
                    break

            if next_use_index == -1:
                return frame_index

            distance = next_use_index - current_index
            if distance > farthest_next_use:
                farthest_next_use = distance
                victim_frame = frame_index

        return victim_frame

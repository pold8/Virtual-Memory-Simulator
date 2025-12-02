from __future__ import annotations
from typing import Optional

from simulator.base_policy import ReplacementPolicy


class LRUAlgorithm(ReplacementPolicy):

    def select_victim(
        self,
        frames: list[Optional[int]],
        reference_string: list[int],
        current_index: int,
    ) -> int:
        victim_frame = 0
        oldest_distance = -1

        for frame_index, page in enumerate(frames):
            if page is None:
                return frame_index

            last_use_index = -1
            for i in range(current_index - 1, -1, -1):
                if reference_string[i] == page:
                    last_use_index = i
                    break

            if last_use_index == -1:
                return frame_index

            distance = current_index - last_use_index

            if distance > oldest_distance:
                oldest_distance = distance
                victim_frame = frame_index

        return victim_frame

from __future__ import annotations
from dataclasses import dataclass
from typing import List, Optional

from simulator.frame import Frame
from simulator.page_table import PageTable, PageTableEntry
from simulator.base_policy import ReplacementPolicy


@dataclass
class SimulationStepResult:
    step_index: int
    requested_page: int
    hit: bool
    fault: bool
    frame_index: Optional[int]
    evicted_page: Optional[int]
    victim_frame_index: Optional[int]
    frames_snapshot: List[Optional[int]]


class SimulationEngine:

    def __init__(
        self,
        num_frames: int,
        reference_string: List[int],
        policy: ReplacementPolicy,
    ) -> None:
        self.num_frames = num_frames
        self.reference_string = reference_string
        self.policy = policy

        self.frames: List[Frame] = [Frame(index=i) for i in range(num_frames)]
        self.page_table = PageTable()

        self.current_step: int = 0

    def get_state(self):
        return self._frames_as_page_list()

    def _find_free_frame(self) -> Optional[Frame]:
        for f in self.frames:
            if f.is_free:
                return f
        return None

    def _frames_as_page_list(self) -> List[Optional[int]]:
        return [f.page for f in self.frames]

    def has_finished(self) -> bool:
        return self.current_step >= len(self.reference_string)


    def step(self) -> SimulationStepResult:
        if self.has_finished():
            raise StopIteration("Simulation is already finished.")

        page = self.reference_string[self.current_step]
        pte: PageTableEntry = self.page_table.get_or_create(page)

        hit = False
        fault = False
        frame_index: Optional[int] = None
        victim_frame_index: Optional[int] = None
        evicted_page: Optional[int] = None

        if pte.present and pte.frame_index is not None:
            hit = True

            frame_index = pte.frame_index
            frame = self.frames[frame_index]
            frame.last_access_time = self.current_step
            pte.referenced = True

        else:
            fault = True

            free_frame = self._find_free_frame()
            if free_frame is not None:
                frame = free_frame
            else:
                frames_pages = self._frames_as_page_list()
                victim_frame_index = self.policy.select_victim(
                    frames_pages,
                    self.reference_string,
                    self.current_step,
                )
                frame = self.frames[victim_frame_index]
                evicted_page = frame.page

                if evicted_page is not None:
                    old_pte = self.page_table.get_or_create(evicted_page)
                    old_pte.present = False
                    old_pte.frame_index = None
                    old_pte.referenced = False

            frame.page = page
            frame.loaded_time = self.current_step
            frame.last_access_time = self.current_step

            pte.present = True
            pte.frame_index = frame.index
            pte.referenced = True

            frame_index = frame.index

        result = SimulationStepResult(
            step_index=self.current_step,
            requested_page=page,
            hit=hit,
            fault=fault,
            frame_index=frame_index,
            evicted_page=evicted_page,
            victim_frame_index=victim_frame_index,
            frames_snapshot=self._frames_as_page_list(),
        )

        self.current_step += 1
        return result

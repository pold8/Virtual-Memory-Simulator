from typing import List, Optional
from simulator.frame import Frame
from simulator.page_table import PageTable
from simulator.simulation_step_result import SimulationStepResult
from simulator.base_policy import ReplacementPolicy
from simulator.vm_config import VMConfig


class SimulationEngine:

    def __init__(
        self,
        vm_config: VMConfig,
        reference_string: List[tuple[int, str]],
        policy: ReplacementPolicy
    ):
        self.cfg = vm_config
        self.reference_string = reference_string
        self.policy = policy

        self.frames: List[Frame] = [Frame(i) for i in range(self.cfg.num_frames)]
        self.page_table = PageTable()

        self.current_step: int = 0

    def _find_free_frame(self) -> Optional[Frame]:
        for f in self.frames:
            if f.is_free:
                return f
        return None

    def _frames_as_list(self):
        return [f.page for f in self.frames]

    def has_finished(self):
        return self.current_step >= len(self.reference_string)

    def step(self) -> SimulationStepResult:
        if self.has_finished():
            raise StopIteration("Simulation finished")

        virtual_address, operation = self.reference_string[self.current_step]

        page = virtual_address // self.cfg.page_size
        offset = virtual_address % self.cfg.page_size

        pte = self.page_table.get_or_create(page)

        hit = False
        fault = False
        evicted_page = None
        victim_frame_index = None
        frame_index = None

        # PAGE HIT
        if pte.present and pte.frame_index is not None:
            hit = True
            frame = self.frames[pte.frame_index]
            frame.last_access_time = self.current_step
            pte.referenced = True
            if operation == "W":
                pte.dirty = True
            frame_index = pte.frame_index

        else:
            # PAGE FAULT
            fault = True

            free_frame = self._find_free_frame()
            if free_frame:
                frame = free_frame
            else:
                # Replacement needed
                victim_frame_index = self.policy.select_victim(
                    self._frames_as_list(),
                    [addr for addr, _ in self.reference_string],
                    self.current_step
                )
                frame = self.frames[victim_frame_index]
                evicted_page = frame.page

                # Clear old PTE
                old_pte = self.page_table.get_or_create(evicted_page)
                old_pte.present = False
                old_pte.frame_index = None
                old_pte.referenced = False
                old_pte.dirty = False

            # Load new page
            frame.page = page
            frame.loaded_time = self.current_step
            frame.last_access_time = self.current_step

            pte.present = True
            pte.frame_index = frame.index
            pte.referenced = True
            if operation == "W":
                pte.dirty = True

            frame_index = frame.index

        result = SimulationStepResult(
            step_index=self.current_step,
            virtual_address=virtual_address,
            operation=operation,
            page=page,
            offset=offset,
            hit=hit,
            fault=fault,
            frame_index=frame_index,
            evicted_page=evicted_page,
            victim_frame_index=victim_frame_index,
            frames_snapshot=self._frames_as_list()
        )

        self.current_step += 1
        return result

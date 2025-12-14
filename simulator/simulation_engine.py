from typing import List, Optional
from simulator.vm_config import VMConfig
from simulator.tlb import TLB
from simulator.page_table import PageTable
from simulator.frame import Frame
from simulator.simulation_step_result import SimulationStepResult
from simulator.base_policy import ReplacementPolicy


class SimulationEngine:

    def __init__(
        self,
        vm_config: VMConfig,
        reference_string: List[tuple[int, str]],   # (VA, R/W)
        policy: ReplacementPolicy,
        tlb_entries: int
    ):
        self.cfg = vm_config
        self.reference_string = reference_string
        self.policy = policy

        self.tlb = TLB(tlb_entries)
        self.frames: List[Frame] = [Frame(i) for i in range(self.cfg.num_frames)]
        self.page_table = PageTable()

        self.current_step = 0

    def _find_free_frame(self) -> Optional[Frame]:
        for f in self.frames:
            if f.is_free:
                return f
        return None

    def _frames_snapshot(self):
        return [f.page for f in self.frames]

    def has_finished(self):
        return self.current_step >= len(self.reference_string)

    def step(self) -> SimulationStepResult:
        if self.has_finished():
            raise StopIteration("Simulation finished.")

        virtual_address, operation = self.reference_string[self.current_step]

        page = virtual_address >> self.cfg.offset_bits
        offset = virtual_address & (self.cfg.page_size - 1)

        tlb_frame = self.tlb.lookup(page, self.current_step)
        tlb_hit = tlb_frame is not None
        write_back = False
        
        victim_frame_index = None
        evicted_page = None

        if tlb_hit:
            frame_index = tlb_frame
            frame = self.frames[frame_index]
            frame.last_access_time = self.current_step
            pte = self.page_table.get_or_create(page)

            pte.referenced = True
            if operation == "W":
                pte.dirty = True

            hit = True
            fault = False

        else:
            pte = self.page_table.get_or_create(page)

            if pte.present:
                hit = True
                fault = False

                frame_index = pte.frame_index
                frame = self.frames[frame_index]
                frame.last_access_time = self.current_step
                pte.referenced = True
                if operation == "W":
                    pte.dirty = True

                self.tlb.insert(page, frame_index, self.current_step)

            else:
                hit = False
                fault = True

                free_frame = self._find_free_frame()
                evicted_page = None
                victim_frame_index = None

                if free_frame:
                    frame = free_frame
                else:
                    frames_list = self._frames_snapshot()
                    victim_frame_index = self.policy.select_victim(
                        frames_list,
                        [addr >> self.cfg.offset_bits for addr, _ in self.reference_string],  # Fix: pass pages
                        self.current_step
                    )
                    frame = self.frames[victim_frame_index]

                    evicted_page = frame.page
                    old_pte = self.page_table.get_or_create(evicted_page)
                    
                    if old_pte.dirty:
                        write_back = True
                    
                    old_pte.present = False
                    old_pte.frame_index = None
                    old_pte.referenced = False
                    old_pte.dirty = False

                    if evicted_page in self.tlb.entries:
                        del self.tlb.entries[evicted_page]

                frame.page = page
                frame.loaded_time = self.current_step
                frame.last_access_time = self.current_step

                pte.present = True
                pte.frame_index = frame.index
                pte.referenced = True
                if operation == "W":
                    pte.dirty = True

                frame_index = frame.index

                self.tlb.insert(page, frame_index, self.current_step)

        result = SimulationStepResult(
            step_index=self.current_step,
            virtual_address=virtual_address,
            operation=operation,
            page=page,
            offset=offset,
            hit=hit,
            fault=fault,
            tlb_hit=tlb_hit,
            frame_index=frame_index,
            victim_frame_index=victim_frame_index if not tlb_hit else None,
            evicted_page=evicted_page if not tlb_hit else None,
            write_back=write_back,
            frames_snapshot=self._frames_snapshot()
        )

        self.current_step += 1
        return result

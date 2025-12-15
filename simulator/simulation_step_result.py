from dataclasses import dataclass
from typing import List, Optional

@dataclass
class SimulationStepResult:
    step_index: int
    virtual_address: int
    operation: str
    page: int
    offset: int
    hit: bool
    fault: bool
    tlb_hit: bool
    frame_index: Optional[int]
    victim_frame_index: Optional[int]
    evicted_page: Optional[int]
    write_back: bool
    frames_snapshot: List[Optional[int]]
